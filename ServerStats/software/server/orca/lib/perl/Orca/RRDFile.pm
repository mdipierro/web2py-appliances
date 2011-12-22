# Orca::RRDFile: Manage RRD file creation and updating.
#
# $HeadURL: file:///var/www/svn/repositories-public/orcaware-public/orca/trunk/lib/Orca/RRDFile.pm $
# $LastChangedRevision: 513 $
# $LastChangedDate: 2005-11-27 21:48:49 -0800 (Sun, 27 Nov 2005) $
# $LastChangedBy: blair@orcaware.com $
#
# Copyright (C) 1998-1999 Blair Zajac and Yahoo!, Inc.
# Copyright (C) 1999-2005 Blair Zajac.
#
# This file is part of Orca.
#
# Orca is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Orca is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Orca in the COPYING-GPL file; if not, write to the Free
# Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# 02111-1307 USA

package Orca::RRDFile;

use strict;
use Carp;
use RRDs;
use Orca::Constants qw($opt_verbose
                       $ORCA_RRD_VERSION
                       @RRA_PDP_COUNTS
                       @RRA_ROW_COUNTS
                       $INCORRECT_NUMBER_OF_ARGS);
use Orca::Config    qw(%config_global
                       @config_groups
                       @config_groups_names
                       @config_plots);
use Orca::Utils     qw(name_to_fsname recursive_mkdir);
use vars            qw($VERSION);

$VERSION = (substr q$Revision: 513 $, 10)/100.0;

# Use a blessed reference to an array as the storage for this class.
# Define these constant subroutines as indexes into the array.  If the
# order of these indexes change, make sure to rearrange the
# constructor in new.
sub I_RRD_FILENAME     () { 0 }
sub I_DATA_EXPRESSION  () { 1 }
sub I_NEW_DATA         () { 2 }
sub I_CREATED_IMAGES   () { 3 }
sub I_PLOT_REF         () { 4 }
sub I_DATA_NUMBER      () { 5 }
sub I_INTERVAL         () { 6 }
sub I_RRD_VERSION      () { 7 }
sub I_CHOOSE_DATA_SUBS () { 8 }
sub I_RRD_UPDATE_TIME  () { 9 }

sub new {
  unless (@_ == 6) {
    confess "$0: Orca::RRDFile::new $INCORRECT_NUMBER_OF_ARGS";
  }

  my ($class,
      $group_index,
      $subgroup_name,
      $data_expression,
      $plot_ref,
      $data_number) = @_;

  # Escape any special characters from the data expression and do some
  # replacements to make the name shorter.  Leave space at the end of
  # the name to append '.rrd'.
  $data_expression = name_to_fsname($data_expression, 4);

  # Create the path to the RRD directory and filename.
  my $group_name = $config_groups_names[$group_index];
  my $dir = "$config_global{rrd_dir}/" .
            name_to_fsname("${group_name}_${subgroup_name}", 0);
  unless (-d $dir) {
    warn "$0: making directory '$dir'.\n";
    recursive_mkdir($dir);
  }
  my $rrd_filename = "$dir/$data_expression.rrd";

  # Create the new object.
  my $self = bless [
    $rrd_filename,
    $data_expression,
    {},
    {},
    $plot_ref,
    $data_number,
    int($config_groups[$group_index]{interval}+0.5),
    $ORCA_RRD_VERSION,
    {},
    -2
  ], $class;

  # See if the RRD file meets two requirements. The first is to see if
  # the last update time can be sucessfully read.  The second is to
  # see if the RRD has an DS named "Orca$ORCA_RRD_VERSION".  If
  # neither one of these is true, then create a brand new RRD is
  # created when data is first flushed to it.
  if (-e $rrd_filename) {
    my $update_time = RRDs::last $rrd_filename;
    if (my $error = RRDs::error) {
      warn "$0: RRDs::last error: '$rrd_filename' $error\n";
    } else {
      if (open(RRDFILE, "<$rrd_filename")) {
        my $version = '';
        while (<RRDFILE>) {
          if (/Orca(\d{8})/) {
            $version = $1;
            last;
          }
        }
        close(RRDFILE) or
          warn "$0: error in closing '$rrd_filename' for reading: $!\n";

        # Compare the version number of file to the required version.
        if (length($version)) {
          if ($version >= $ORCA_RRD_VERSION) {
            $self->[I_RRD_UPDATE_TIME] = $update_time;
            $self->[I_RRD_VERSION]     = $version;
          } else {
            warn "$0: old version $version RRD '$rrd_filename' found: will ",
                  "create new version $ORCA_RRD_VERSION file.\n";
          }
        } else {
          warn "$0: unknown version RRD '$rrd_filename' found: will create ",
               "new version $ORCA_RRD_VERSION file.\n";
        }
      }
    }
  }

  $self;
}

sub version {
  $_[0]->[I_RRD_VERSION];
}

sub filename {
  $_[0]->[I_RRD_FILENAME];
}

sub data_expression {
  $_[0]->[I_DATA_EXPRESSION];
}

sub rrd_update_time {
  $_[0]->[I_RRD_UPDATE_TIME];
}

sub add_image {
  my ($self, $image) = @_;
  $self->[I_CREATED_IMAGES]{$image->name} = $image;
  $self;
}

sub created_images {
  values %{$_[0]->[I_CREATED_IMAGES]};
}

# Queue a list of (time, value) data pairs.  Return the number of data
# pairs sucessfully queued.
# Call: $self->(unix_epoch_time1, value1, unix_epoch_time2, value2, ...);
sub queue_data {
  my $self = shift;

  my $count = 0;
  my $rrd_update_time = $self->[I_RRD_UPDATE_TIME];
  while (@_ > 1) {
    my ($time, $value) = splice(@_, 0, 2);
    next if $time <= $rrd_update_time;
    $self->[I_NEW_DATA]{$time} = $value;
    ++$count;
  }

  $count;
}

sub flush_data {
  my $self = shift;

  # Get the times of the new data to put into the RRD file.
  my @times = sort { $a <=> $b } keys %{$self->[I_NEW_DATA]};

  return unless @times;

  my $rrd_filename = $self->[I_RRD_FILENAME];

  # Create the Orca data file if it needs to be created.
  if ($self->[I_RRD_UPDATE_TIME] == -2) {

    # Assume that a maximum of two time intervals are needed before a
    # data source value is set to unknown.
    my $interval    = $self->[I_INTERVAL];
    my $data_number = $self->[I_DATA_NUMBER];
    my $data_source = "DS:Orca$ORCA_RRD_VERSION:"                  .
                      $self->[I_PLOT_REF]{data_type}[$data_number] .
                      sprintf(":%d:", 2*$interval)                 .
                      $self->[I_PLOT_REF]{data_min}[$data_number]  .
                      ':'                                          .
                      $self->[I_PLOT_REF]{data_max}[$data_number];
    my @options = ($rrd_filename,
                   '-b', $times[0]-1,
                   '-s', $interval,
                   $data_source);

    # Create the round robin archives.  Take special care to not
    # create two RRA's with the same number of primary data points.
    # This can happen if the interval is equal to one of the
    # consolidated intervals.
    my $count          = int($RRA_ROW_COUNTS[0]*300.0/$interval + 0.5);
    my @one_pdp_option = ("RRA:AVERAGE:0.5:1:$count");

    for (my $i=1; $i<@RRA_PDP_COUNTS; ++$i) {
      next if $interval > 300*$RRA_PDP_COUNTS[$i];
      my $rra_pdp_count = int($RRA_PDP_COUNTS[$i]*300.0/$interval + 0.5);
      if (@one_pdp_option and $rra_pdp_count != 1) {
        push(@options, @one_pdp_option);
      }
      @one_pdp_option = ();
      push(@options, "RRA:AVERAGE:0.5:$rra_pdp_count:$RRA_ROW_COUNTS[$i]");
    }

    # Now do the actual creation.
    if ($opt_verbose) {
      print "  Creating RRD '$rrd_filename'";
      if ($opt_verbose > 2) {
        print " with options ", join(' ', @options[1..$#options]);
      }
      print ".\n";
    }
    RRDs::create @options;

    if (my $error = RRDs::error) {
      warn "$0: RRDs::create(", join(', ', @options), ") failed: $error\n";
      return;
    }
  }

  # Flush all of the stored data into the RRD file.
  my @options;
  my $old_rrd_update_time = $self->[I_RRD_UPDATE_TIME];
  foreach my $time (@times) {
    push(@options, "$time:" . $self->[I_NEW_DATA]{$time});
  }
  RRDs::update $rrd_filename, @options;
  my $ok = 1;
  if (my $error = RRDs::error) {
    warn "$0: warning: cannot put data starting at ",
         scalar localtime($times[0]),
         " ($times[0]) into '$rrd_filename': $error\n";
    return 0;
  }

  # If there were no errors, then totally clear the hash to save
  # memory.
  undef $self->[I_NEW_DATA];
  $self->[I_NEW_DATA] = {};

  $self->[I_RRD_UPDATE_TIME] = $times[-1];

  1;
}

1;
