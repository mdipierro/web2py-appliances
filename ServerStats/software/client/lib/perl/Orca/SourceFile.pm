# Orca::SourceFile: Manage the watching and loading of source data files.
#
# $HeadURL: file:///var/www/svn/repositories-public/orcaware-public/orca/trunk/lib/Orca/SourceFile.pm $
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

package Orca::SourceFile;

use strict;
use Carp;
use Digest::MD5         qw(md5);
use Storable            qw(dclone);
use Orca::Constants     qw($opt_verbose
                           die_when_called
                           $INCORRECT_NUMBER_OF_ARGS);
use Orca::Config        qw(%config_global
                           @config_groups
                           @config_groups_names
                           @config_plots
                           data_index_to_color);
use Orca::OldState      qw($orca_old_state);
use Orca::DataFile      qw(ORCA_DATAFILE_LAST_INDEX);
use Orca::OpenFileHash  qw($open_file_cache);
use Orca::SourceFileIDs qw(@sfile_fids);
use Orca::ImageFile;
use Orca::RRDFile;
use Orca::Utils         qw(email_message);
use vars                qw(@ISA $VERSION);

@ISA     = qw(Orca::DataFile);
$VERSION = (substr q$Revision: 513 $, 10)/100.0;

# This is a static variable that lists all of the column names for a
# particular group.
my @group_column_names;

# This caches the reference to the array holding the column
# descriptions for files that have their column descriptions in the
# first line of the file.
my %first_line_cache;

# These are caches for the different objects that are used to add a
# plot.
my %all_rrds_cache;
my %my_rrd_list_cache;
my %choose_data_sub_cache;

# Use a blessed reference to an array as the storage for this class.
# Since this class is a subclass of Orca::DataFile, append to the
# end of the Orca::DataFile array the values needed by this class
# using the ORCA_DATAFILE_LAST_INDEX index.  Define these constant
# subroutines as indexes into the array.  If the order of these
# indexes change, make sure to rearrange the constructor in new.
sub I_GROUP_INDEX        () { ORCA_DATAFILE_LAST_INDEX +  1 }
sub I_INTERVAL           () { ORCA_DATAFILE_LAST_INDEX +  2 }
sub I_LATE_INTERVAL      () { ORCA_DATAFILE_LAST_INDEX +  3 }
sub I_READ_INTERVAL      () { ORCA_DATAFILE_LAST_INDEX +  4 }
sub I_REOPEN             () { ORCA_DATAFILE_LAST_INDEX +  5 }
sub I_DATE_SOURCE        () { ORCA_DATAFILE_LAST_INDEX +  6 }
sub I_DATE_PARSE         () { ORCA_DATAFILE_LAST_INDEX +  7 }
sub I_MY_RRD_LIST        () { ORCA_DATAFILE_LAST_INDEX +  8 }
sub I_ALL_RRD_REF        () { ORCA_DATAFILE_LAST_INDEX +  9 }
sub I_GROUP_KEYS         () { ORCA_DATAFILE_LAST_INDEX + 10 }
sub I_CHOOSE_DATA_SUB    () { ORCA_DATAFILE_LAST_INDEX + 11 }
sub I_COLUMN_DESCRIPTION () { ORCA_DATAFILE_LAST_INDEX + 12 }
sub I_LAST_DATA_TIME     () { ORCA_DATAFILE_LAST_INDEX + 13 }
sub I_LAST_READ_TIME     () { ORCA_DATAFILE_LAST_INDEX + 14 }
sub I_FIRST_LINE         () { ORCA_DATAFILE_LAST_INDEX + 15 }
sub I_DATE_COLUMN_INDEX  () { ORCA_DATAFILE_LAST_INDEX + 16 }
sub I_IS_CURRENT         () { ORCA_DATAFILE_LAST_INDEX + 17 }
sub I_IS_CURRENT_DAY     () { ORCA_DATAFILE_LAST_INDEX + 18 }

sub new {
  unless (@_ == 3) {
    confess "$0: Orca::SourceFile::new passed $INCORRECT_NUMBER_OF_ARGS";
  }

  my ($class, $group_index, $fid) = @_;

  my $self = $class->SUPER::new($fid);

  my $config_group = $config_groups[$group_index];

  # Set the last value to preexpand the array.
  $self->[I_IS_CURRENT_DAY]     = undef;
  $self->[I_GROUP_INDEX]        = $group_index;
  $self->[I_INTERVAL]           = $config_group->{interval};
  $self->[I_LATE_INTERVAL]      = $config_group->{late_interval};
  $self->[I_READ_INTERVAL]      = $config_group->{read_interval};
  $self->[I_REOPEN]             = $config_group->{reopen};
  $self->[I_DATE_SOURCE]        = $config_group->{date_source};
  $self->[I_DATE_PARSE]         = $config_group->{date_parse};
  $self->[I_MY_RRD_LIST]        = [];
  $self->[I_ALL_RRD_REF]        = undef;
  $self->[I_GROUP_KEYS]         = {};
  $self->[I_CHOOSE_DATA_SUB]    = undef;

  $self->[I_COLUMN_DESCRIPTION] = $config_group->{column_description};
  $self->[I_LAST_DATA_TIME]     = -1;
  $self->[I_LAST_READ_TIME]     = -1;
  $self->[I_FIRST_LINE]         =  0;
  $self->[I_DATE_COLUMN_INDEX]  = undef;

  # Load in any state information for this file.
  my $filename = $sfile_fids[$fid];
  my @column_description;
  if (defined (my $ref = delete $orca_old_state->{$filename})) {
    @$self[I_LAST_DATA_TIME,
           I_LAST_READ_TIME,
           &Orca::DataFile::I_FILE_DEV,
           &Orca::DataFile::I_FILE_INO,
           &Orca::DataFile::I_FILE_SIZE,
           &Orca::DataFile::I_FILE_MTIME] = splice(@$ref, 0, 6);
    @column_description = @{$ref->[0]} if $ref->[0];
  }

# XXXXX
#  # Do the following steps if the source data file exists.  If there is
#  # no entry in the state database for this file, then create a default
#  # one.  If there is an entry, then check the file's mtime and if they
#  # do not agree, then make the entry a default one so that the data from
#  # it will be reloaded.  If the source data file does not exist, then
#  # make the entry a default one.
#  my $state;
#  if ($self->status == -1) {
#    $state = Orca::
#  } else {
#  }
#  # If the source data file does not exist in the state database, then
#  # create a new default entry.  If the file does not exist, then reset to
#  # If the source file's mtime is the same as stored in the saved
#  # state file, then load all the information from it, otherwise do
#  # not keep any of it and load the file freshly.
#  if ($orca_
#  if (my $mtime = delete($state->{_file_mtime}) eq $self->file_mtime) {
#    while (my ($key, $value) = each %$state) {
#      $self->[$key] = $value;
#    }
#  }

  # Now do a stat of the file.
  my $stat_status = $self->status;

  # Load the column names if the column names are supposed to be loaded
  # from the file.  Use the cached names if the file has not changed.
  if ($self->[I_COLUMN_DESCRIPTION][0] eq 'first_line') {
    if ($stat_status or !@column_description) {
      my $fd = $open_file_cache->open($fid, $self->file_mtime);
      return unless $fd;
      my $line = <$fd>;
      chomp($line);
      if ($line) {
        $self->[I_FIRST_LINE] = 1;
        @column_description = split(' ', $line);
      } else {
        warn "$0: warning: no first_line for '$filename' yet.\n";
        $open_file_cache->close($fid) or
          warn "$0: warning: cannot close '$filename' for reading: $!\n";
        return;
      }
    }
    my $cache_key = md5(join("\200", @column_description));
    unless (defined $first_line_cache{$cache_key}) {
      $first_line_cache{$cache_key} = \@column_description;
    }
    $self->[I_COLUMN_DESCRIPTION] = $first_line_cache{$cache_key};
  }

  # Test if the file has been updated in the last _interval number of
  # seconds.  If so, then note it so we can see when the file is no
  # longer being updated.
  $self->[I_IS_CURRENT] = $self->is_current;

  return unless $self->get_date_column;

  $self;
}

# For each group make a note of the column description names that appear.
sub add_groups {
  my $self = shift;

  foreach my $group_index (@_) {
    $self->[I_GROUP_KEYS]{$group_index} = 1;
    foreach my $description (@{$self->[I_COLUMN_DESCRIPTION]}) {
      $group_column_names[$group_index]{$description} = 1;
    }
  }
}

# Return 1 if the source data file is current or 0 otherwise.  Also
# note the day that this test was performed.  This lets the code
# ignore files that are not current because a new file was generated
# for the next day.
sub is_current {
  my $self = shift;

  $self->[I_IS_CURRENT_DAY] = (localtime)[3];

  $self->last_stat_time <= $self->file_mtime + $self->[I_LATE_INTERVAL];
}

# This returns the time when the file should be next read.  To
# calculate the next read time, take into the account the time that it
# takes for the file to be updated.  In some sense, this is measured
# by the late interval.  Because we won't want to use the complete
# late interval, take the multiplicative average instead of the
# summation average, since the multiplicative average will result in
# an average closer to the smaller of the two values.  If the source
# file is current, then just add the modified late interval to the
# last file modification time, otherwise add the late interval to the
# last file stat time.  Use the late interval to watch old files so we
# don't spend as much time on them.
sub next_load_time {
  my $self = shift;

  my $last_stat_time = $self->last_stat_time;
  my $file_mtime     = $self->file_mtime;

  if ($last_stat_time <= $file_mtime + $self->[I_LATE_INTERVAL]) {
    return $file_mtime + $self->[I_READ_INTERVAL];
  } else {
    return $last_stat_time + $self->[I_LATE_INTERVAL];
  }
}

sub get_date_column {
  my $self = shift;

  return $self if $self->[I_DATE_SOURCE][0] eq 'file_mtime';

  my $fid              = $self->fid;
  my $date_column_name = $self->[I_DATE_SOURCE][1];

  my $found = -1;
  for (my $i=0; $i<@{$self->[I_COLUMN_DESCRIPTION]}; ++$i) {
    if ($self->[I_COLUMN_DESCRIPTION][$i] eq $date_column_name) {
      $found = $i;
      last;
    }
  }

  unless ($found > -1) {
    warn "$0: warning: cannot find date '$date_column_name' in ",
         "'$sfile_fids[$fid]'.\n";
    warn "@{$self->[I_COLUMN_DESCRIPTION]}\n";
    return;
  }
  $self->[I_DATE_COLUMN_INDEX] = $found;

  $self;
}

# XXX
# Utility function make a deep clone one of the plots in the
# config_plots array, except for the 'created_orca_images' hash key.
# This should really be a method for a single plot, but the plot is
# not an object right now, so it doesn't have any methods that can be
# given to it.
sub deep_clone_plot {
  my $plot                        = shift;
  my $restore_created_orca_images = shift;

  # Be careful not to make a deep copy of the 'created_orca_images'
  # reference, since it can cause recursion.
  my $created_orca_images      = delete $plot->{created_orca_images};
  my $new_plot                 = dclone($plot);
  $plot->{created_orca_images} = $created_orca_images;
  if ($restore_created_orca_images) {
    $new_plot->{created_orca_images} = $created_orca_images;
  }

  if (wantarray) {
    ($new_plot, $created_orca_images);
  } else {
    $new_plot;
  }
}

sub add_plots {
  # Make sure that the user has called the add_groups method and
  # inserted at least one key.
  unless (@group_column_names) {
    confess "$0: Orca::SourceFile::add_groups must be called before ",
            "add_plots.\n";
  }

  unless (@_ == 5) {
    confess "$0: Orca::SourceFile::add_plots $INCORRECT_NUMBER_OF_ARGS";
  }

  my ($self,
      $group_index,
      $subgroup_name,
      $rrd_data_files_ref,
      $image_files_ref) = @_;

  my $group_name = $config_groups_names[$group_index];

  # See if we have already done all the work for a plot with this group_name,
  # subgroup_name, and column description.  Use an MD5 hash instead of a very
  # long key.  Store into a hash the column names found in this file for this
  # group.  Finally, create a hash keyed by column name with a value of the
  # index into the column description array.
  my @column_description = @{$self->[I_COLUMN_DESCRIPTION]};
  my %column_description;
  for (my $i=0; $i<@column_description; ++$i) {
    $column_description{$column_description[$i]} = $i;
  }
  my $plot_key  = join("\200", $group_name,
                               $subgroup_name,
                               @column_description);
  my $cache_key = md5($plot_key);
  if (defined $all_rrds_cache{$cache_key}) {
    $self->[I_ALL_RRD_REF]     = $all_rrds_cache{$cache_key};
    $self->[I_MY_RRD_LIST]     = $my_rrd_list_cache{$cache_key};
    $self->[I_CHOOSE_DATA_SUB] = $choose_data_sub_cache{$cache_key};
    return 1;
  }

  # Use this hash to keep a list of RRDs that this file uses.
  my %my_rrd_list;

  # This is the source for an anonymous subroutine that given a row
  # from a source data file returns a hash keyed by RRD name with the
  # values calculated from the row.
  my $choose_data_expr = "sub {\n  (\n";

  # Go through each plot to create and process it for this file.
  my @regexp_pos          = map { 0 } (1..@config_plots);
  my $oldest_regexp_index = 0;
  my $handle_regexps      = 0;
  my $i                   = 0;
  my $old_i               = 0;

  # This is the main loop where we keep looking for plots to create
  # until all of the column descriptions have been compared against.
  while ($handle_regexps or $i < @config_plots) {
    # If we've reached an index value greater than the largest index
    # in the plots, then reset the index to the oldest regexp that
    # still needs to be completed.
    if ($handle_regexps and $i >= @config_plots) {
      $i = $oldest_regexp_index;
    }

    my $original_plot = $config_plots[$i];
    my $plot = $original_plot;

    # Skip this plot if the source group indexes does not match.
    # Increment the index of the next plot to handle.
    if ($plot->{source_index} != $group_index) {
      if ($oldest_regexp_index == $i) {
        $handle_regexps = 0;
        ++$oldest_regexp_index;
      }
      ++$i;
      next;
    }

    # There are three cases to handle:
    # 1) Regular expression match in the first data with no additional datas.
    # 2) Regular expression match in the first data with additional datas.
    # 3) All others cases.
    # The first is a single data source that has a regular expression.  In
    # this case, all of the columns are searched to match the regular
    # expression.  This generates a single plot with all of the different
    # data sources plotted on it.  The second case is two or more data
    # sources and where the first data source has a regular expression
    # match.  This may generate more than one plot, for each set of columns
    # that match the regular expression.  The final case to handle is when
    # the previous two cases are not true.  The last column matched on is
    # stored in @regexp_pos.
    my $number_datas         = @{$plot->{data}};
    my $number_elements      = @{$plot->{data}[0]};
    my $regexp_element_index = -1;
    for (my $j=0; $j<$number_elements; ++$j) {
      if ($plot->{data}[0][$j] =~ m:\(.+\):) {
        $regexp_element_index = $j;
        last;
      }
    }

    # 1) Regular expression match in the first data with no additional datas.
    my $plot_has_only_one_data_with_regexp = 0;
    if ($number_datas == 1 and $regexp_element_index != -1) {

      $plot_has_only_one_data_with_regexp = 1;

      # If we've gone up to the last column to match, then go on.
      if ($regexp_pos[$i] >= @column_description) {
        if ($oldest_regexp_index == $i) {
          $handle_regexps = 0;
          ++$oldest_regexp_index;
        }
        $i = $plot->{flush_regexps} ? $oldest_regexp_index : $i + 1;
        next;
      }
      $regexp_pos[$i] = @column_description;

      # Start by making a deep copy of the plot.  Replace the regular
      # expression in the first data with the name of the column that
      # caused the match.
      $plot = deep_clone_plot($plot, 1);

      # At this point we have a copy of plot.  Now go through looking
      # for all the columns that match and create an additional data
      # source for each match.
      my @data_with_regexp = @{$plot->{data}[0]};
      my $regexp           = $data_with_regexp[$regexp_element_index];
      my $new_data_index   = 0;
      my $original_legend  = $plot->{legend}[0];
      foreach my $column_name (@column_description) {
        my @matches = $column_name =~ /$regexp/;
        next unless @matches;

        # Replace the regular expression match with the matched column
        # name.
        $data_with_regexp[$regexp_element_index] = $column_name;
        $plot->{data}[$new_data_index] = [ @data_with_regexp ];

        # Copy any items over that haven't been created for this new
        # data source.  Make sure that any new elements added to
        # pcl_plot_append_elements show up here.  The first data_min,
        # data_max, data_type, and summary_format are always set and
        # if any later ones are not set, then use the previously set
        # one.
        unless (defined $plot->{data_min}[$new_data_index]) {
          $plot->{data_min}[$new_data_index] =
            $plot->{data_min}[$new_data_index-1];
        }
        unless (defined $plot->{data_max}[$new_data_index]) {
          $plot->{data_max}[$new_data_index] =
            $plot->{data_max}[$new_data_index-1];
        }
        unless (defined $plot->{data_type}[$new_data_index]) {
          $plot->{data_type}[$new_data_index] =
            $plot->{data_type}[$new_data_index-1];
        }
        unless (defined $plot->{color}[$new_data_index]) {
          $plot->{color}[$new_data_index] =
            data_index_to_color($new_data_index);
        }
        unless (defined $plot->{legend}[$new_data_index]) {
          $plot->{legend}[$new_data_index] = $original_legend;
        }
        unless (defined $plot->{line_type}[$new_data_index]) {
          $plot->{line_type}[$new_data_index] = $plot->{line_type}[0];
        }
        unless (defined $plot->{summary_format}[$new_data_index]) {
          $plot->{summary_format}[$new_data_index] =
            $plot->{summary_format}[$new_data_index-1];
        }

        # Replace the regular expression in any legend elements.
        my $legend = $plot->{legend}[$new_data_index];
        my $count  = 1;
        foreach my $match (@matches) {
          $legend =~ s/\$$count/$match/ge;
          $legend =~ s/\(.+\)/$match/ge;
          ++$count;
        }
        $plot->{legend}[$new_data_index] = $legend;

        ++$new_data_index;
      }

      if ($oldest_regexp_index == $i) {
        $handle_regexps = 0;
        ++$oldest_regexp_index;
      }
      $old_i = $i;
      $i = $plot->{flush_regexps} ? $oldest_regexp_index : $i + 1;
      next unless $new_data_index;
    }

    # 2) Regular expression match in the first data with additional datas.
    elsif ($number_datas > 1 and $regexp_element_index != -1) {
      $handle_regexps = 1;

      # If we've gone up to the last column to match, then go on.  If
      # this is the oldest regexp, then increment oldest_regexp_index.
      if ($regexp_pos[$i] >= @column_description) {
        if ($oldest_regexp_index == $i) {
          $handle_regexps = 0;
          ++$oldest_regexp_index;
        }
        $i = $plot->{flush_regexps} ? $oldest_regexp_index : $i + 1;
        next;
      }

      # Go through all of the columns and stop at the first match.
      my @data_with_regexp = @{$plot->{data}[0]};
      my $regexp           = $data_with_regexp[$regexp_element_index];
      my $column_description;
      my @matches;
      for (;$regexp_pos[$i]<@column_description; ++$regexp_pos[$i]) {
        @matches = $column_description[$regexp_pos[$i]] =~ /$regexp/;
        if (@matches) {
          $column_description = $column_description[$regexp_pos[$i]];
          last;
        }
      }
      unless (@matches) {
        if ($oldest_regexp_index == $i) {
          ++$oldest_regexp_index;
          $handle_regexps = 0;
        }
        ++$i;
        next;
      }
      ++$regexp_pos[$i];

      # Start by making a deep copy of the plot.  Replace the regular
      # expression in the first data with the name of the column that
      # caused the match.  Then create string form of the plot object
      # using Data::Dumper::Dumper and replace all of the $1, $2,
      # ... with what was matched in the first data source.
      my $created_orca_images;
      ($plot, $created_orca_images) = deep_clone_plot($plot, 0);
      $plot->{data}[0][$regexp_element_index] = $column_description;
      my $d = Data::Dumper->Dump([$plot], [qw(plot)]);
      $plot->{created_orca_images} = $created_orca_images;
      my $count = 1;
      foreach my $match (@matches) {
        $d =~ s/\$$count/$match/mge;
        $d =~ s/\(.+\)/$match/mge;
        ++$count;
      }
      {
        local $SIG{__DIE__}  = 'DEFAULT';
        local $SIG{__WARN__} = \&die_when_called;
        eval $d;
      }
      die "$0: internal error: eval on\n   $d\nOutput: $@\n" if $@;

      # Either increment the index or reset it to the oldest regexp
      # index.
      $old_i = $i;
      $i = $plot->{flush_regexps} ? $oldest_regexp_index : $i + 1;
    }

    # 3) All others cases.
    else {
      $old_i = $i++;
      ++$oldest_regexp_index unless $handle_regexps;
    }

    # Make a copy of the data's so that if we change anything, we're
    # not changing the original plot structure.  Look through each
    # element of each data and look for names appearing in the column
    # description array.  If there is a match for this file, then
    # replace the column name with the Perl code that indexes the @_
    # array for use in a dynamically generated anonymous subroutine.
    # If there is no match, then see if the element matches a name
    # from one of the other column names from other files in the same
    # group.  In this case the data argument for this file will not be
    # used.

    # This hash is keyed by the Perl expression that indexes the @_
    # array in the dynamically generated anonymous subroutine.  The
    # keys of this hash are checked later on to see if the value is
    # undefined or 'U', in which case the subroutine returns 'U'
    # early instead of evaluating the entire data expression.
    my %substituted_values;

    my @datas;
    foreach my $one_data (@{$plot->{data}}) {
      push(@datas, [@$one_data]);
    }
    my $required = $plot->{required};
    for (my $j=0; $j<@datas; ++$j) {
      my $match_one_data = 0;
      for (my $k=0; $k<@{$datas[$j]}; ++$k) {
        my $element = $datas[$j][$k];
        my $pos;
        if (defined ($pos = $column_description{$element})) {
          $match_one_data = 1;
          $datas[$j][$k]  = "\$_[$pos]";
          $substituted_values{"\$_[$pos]"} = 1;
        } elsif (defined $group_column_names[$group_index]{$element}) {
          my $m = $old_i + 1;
          if ($required) {
            warn "$0: $element in 'data @{$plot->{data}[$j]}' in plot #$m ",
                 "not replaced since it is not in file '",
                 $self->filename, "'.\n";
          }
          $datas[$j] = undef;
          last;
        }
      }
      # If there were no substitutions and verbose is on, then warn about it.
      if (!$match_one_data and $opt_verbose > 1) {
        my $m = $old_i + 1;
        warn "$0: warning: no substitutions performed for ",
             "'data @{$plot->{data}[$j]}' in plot #$m in '",
             $self->filename, "'.\n";
      }
    }

    # Because users may place code into the data statements that do
    # not have any substitutions, then the only way to check for the
    # validity is to create valid anonymous subroutines and try them.
    # Invalid ones will either return undef or fail to compile.  If
    # the plot is required, then replace invalid subroutines with one
    # that returns the character 'U', which is RRD's way of declaring
    # undefined data.  Here the results of eval'ing a test subroutine
    # on a data is kept.  The cached result is either a 1 or a 0.  To
    # test the subroutine, pass the newly created subroutine a fake
    # array of numbers, where the array has as many elements as there
    # are in one line from the file.
    my @fake_numbers = 1 .. @column_description;
    my @substituted_data_expressions;
    my $one_ok_data = 0;
    for (my $j=0; $j<@datas; ++$j) {
      my $data_expression;
      if (defined $datas[$j]) {
        my $sub_expr = "sub {\n";
        foreach my $s (sort keys %substituted_values) {
          $sub_expr .= "  if (!defined($s) || $s eq 'U') { return 'U'; }\n";
        }

        # The extra set of parentheses around the data statement are
        # added to cause a compile failure in the subroutine if the
        # column name in the data expression has a # in it and the
        # file does not have that column name in it.  Otherwise, the
        # expression may compile successfully, but return undef.  For
        # example, for the data expression
        #   data #httpds
        # the subroutine will be
        #   sub {
        #     return #httpds;
        #   }
        # Adding the parentheses around '#httpds' will cause a compile
        # failure because the opening parenthesis is not closed.
        $data_expression  = "(@{$datas[$j]})";
        $sub_expr        .= "  $data_expression;\n}";
        my $sub_expr_md5  = md5($data_expression);
        my $eval_result   = $choose_data_sub_cache{$sub_expr_md5};
        unless (defined $eval_result) {
          $eval_result = 1;
          my $test_value;
          my $message;
          {
            local $SIG{__DIE__}  = 'DEFAULT';
            local $SIG{__WARN__} = \&die_when_called;
            if (my $sub = eval $sub_expr) {
              eval { $test_value = &$sub(@fake_numbers) };
            }
          }
          if ($@) {
            $eval_result = 0;
            $@ =~ s/\s+$//g;
            my $m = $old_i + 1;
            $message = "$0: warning: cannot compile\n$sub_expr\nfor " .
                       "plot #$m 'data @{$plot->{data}[$j]}': $@\n";
          } elsif (!defined $test_value) {
            $eval_result = 0;
            my $m = $old_i + 1;
            $message = "$0: warning: testing of\n$sub_expr\nfor " .
                       "plot #$m 'data @{$plot->{data}[$j]}' yielded " .
                       "an undefined value.\n";
          }
          if ($message and ($required or $opt_verbose > 1)) {
            warn $message;
          }
          $choose_data_sub_cache{$sub_expr_md5} = $eval_result;
        }
        $data_expression = undef unless $eval_result;
      }
      # If the data_expression did not work, but the plot is required, then
      # have the expression return 'U';
      if (!$data_expression and $plot->{required}) {
        $data_expression = "'U'";
      }
      $one_ok_data = 1 if $data_expression;
      push(@substituted_data_expressions, $data_expression);
    }

    # If none of the data expressions compiled, then go on to the next
    # unless the plot is required.
    next if (!$one_ok_data and !$required);

    # At this point we have a plot to create.

    # For each valid data source in this plot, place each the substituted
    # code a large anonymous subroutine that takes a single row of data
    # from an input source file and returns a hash keyed by the name
    # used for a RRD and the value calculated using the input row of
    # data.  Also create an unique Orca data file name for this plot
    # and a name for this plot that does not include the subgroup name.
    my @my_rrds;
    my @my_short_rrds;
    my @names_with_subgroup;
    my @names_without_subgroup;
    my $previous_data_type     = '';
    my $previous_group_index   = -1;
    my $previous_subgroup_name = '';
    for (my $j=0; $j<@substituted_data_expressions; ++$j) {

      # Include in the original data expression the data_type that RRD
      # will apply to the input data.
      my $data_type                   = lc($plot->{data_type}[$j]);
      my $original_data_expression    = join('_', @{$plot->{data}[$j]});
      my $substituted_data_expression = $substituted_data_expressions[$j];

      my $name_with_subgroup          = join('_',
                                             $group_name,
                                             $subgroup_name,
                                             $data_type,
                                             $original_data_expression);
      my $name_without_subgroup       = join('_',
                                             $group_name,
                                             $data_type,
                                             $original_data_expression);
      push(@names_with_subgroup,    $name_with_subgroup);
      push(@names_without_subgroup, $name_without_subgroup);

      # If the current data expression is very similar to the previous
      # one, then do not include the group, subgroup and data_type.
      my $short_name_with_subgroup;
      if ($group_index == $previous_group_index) {
        $short_name_with_subgroup  = '_';
      } else {
        $short_name_with_subgroup  = "${group_name}_";
        $previous_group_index      = $group_index;
      }
      if ($subgroup_name eq $previous_subgroup_name) {
        $short_name_with_subgroup .= '_';
      } else {
        $short_name_with_subgroup .= "${subgroup_name}_";
        $previous_subgroup_name    = $subgroup_name;
      }
      if ($data_type eq $previous_data_type) {
        $short_name_with_subgroup .= '_';
      } else {
        $short_name_with_subgroup .= "${data_type}_";
        $previous_data_type        = $data_type;
      }
      $short_name_with_subgroup   .= $original_data_expression;

      # Create a new RRD only if it doesn't already exist and if a
      # valid get data subroutine is created.  Keep the
      # choose_data_sub for this file.
      if (defined $substituted_data_expression) {
        $choose_data_expr .= "    '$name_with_subgroup', " .
                             "$substituted_data_expression,\n";
        unless (defined $rrd_data_files_ref->{$name_with_subgroup}) {
          my $rrd_file = Orca::RRDFile->new($group_index,
                                            $subgroup_name,
                                            "${data_type}_${original_data_expression}",
                                            $plot,
                                            $j);
          $rrd_data_files_ref->{$name_with_subgroup} = $rrd_file;
        }
        $self->[I_ALL_RRD_REF]            = $rrd_data_files_ref;
        $my_rrd_list{$name_with_subgroup} = 1;
        push(@my_rrds, $name_with_subgroup);
        push(@my_short_rrds, $short_name_with_subgroup);
      }
    }

    # Generate a name for this image that is used to look up already
    # created Orca::Image objects.  Normally, the name will contain
    # all the column names that matched the data lines in the
    # configuration file.  However, if a plot has only one data line
    # and that data line has a regular expression match in it, then
    # this method will generate a different image for all input data
    # files that contain different combinations of matching column
    # names.  For this case, do not store the column names that match,
    # use a stringified form of the original data line with a
    # 'volatile' tag in it to help ensure that there are no name
    # collisions.  Also, shorten the two arrays that contain the
    # matching column names to a contain single element with the name
    # of the data line that generated the image with no mention of the
    # names of the matched columns.
    my $all_names_with_subgroup;
    if ($plot_has_only_one_data_with_regexp) {
      $all_names_with_subgroup = join('_',
                                      $group_name,
                                      $subgroup_name,
                                      lc($plot->{data_type}[0]),
                                      'volatile',
                                      @{$original_plot->{data}[0]});

      # Because the regular expression in the configuration file is
      # placed in these variables and these variables are used to
      # generate the HTML and image filenames and hence the URLs, some
      # characters will prevent the web server from properly serving
      # the files.  Notably, the ? character will cause the web server
      # to parse any following characters as part of the CGI query
      # string and as not part of the filename, hence a 404 will be
      # returned.
      $all_names_with_subgroup =~ s/\?/q/g;

      @my_short_rrds = ($all_names_with_subgroup);
      @names_without_subgroup = map { s/\?/q/g; $_ }
                                (join('_',
                                      $group_name,
                                      lc($plot->{data_type}[0]),
                                      'volatile',
                                      @{$original_plot->{data}[0]}));
    } else {
      $all_names_with_subgroup = join(',', sort @names_with_subgroup);
    }

    my $image = $image_files_ref->{hash}{$all_names_with_subgroup};
    if (defined $image) {
      if ($plot_has_only_one_data_with_regexp) {
        $image->add_additional_plot($plot);
      }
      $image->add_rrds(@my_rrds);
    } else {
      $image = Orca::ImageFile->new($group_index,
                                    $subgroup_name,
                                    join(',', @my_short_rrds),
                                    join(',', @names_without_subgroup),
                                    $plot,
                                    $rrd_data_files_ref,
                                    \@my_rrds);
      $image_files_ref->{hash}{$all_names_with_subgroup} = $image;
      push(@{$image_files_ref->{list}}, $image);
      push(@{$config_plots[$old_i]{created_orca_images}}, $image);
    }

    # Put into each RRD the images that are generated from it.
    foreach my $rrd_key (@my_rrds) {
      $rrd_data_files_ref->{$rrd_key}->add_image($image);
    }
  }

  $choose_data_expr .= "  );\n}\n";
  {
    local $SIG{__DIE__}        = 'DEFAULT';
    local $SIG{__WARN__}       = \&die_when_called;
    $self->[I_CHOOSE_DATA_SUB] = eval $choose_data_expr;
  }
  if ($@) {
    my $m = $old_i + 1;
    die "$0: warning: bad evaluation of command for plot #$m:\n",
        "$choose_data_expr\nOutput: $@\n";
  }

  $all_rrds_cache{$cache_key}        = $self->[I_ALL_RRD_REF];
  $choose_data_sub_cache{$cache_key} = $self->[I_CHOOSE_DATA_SUB];
  my $tmp                            = [sort keys %my_rrd_list];
  $my_rrd_list_cache{$cache_key}     = $tmp;
  $self->[I_MY_RRD_LIST]             = $tmp;

  1;
}

sub load_new_data {
  my $self = shift;

  my $fid = $self->fid;

  # Test to see if we should read the file.  If the file has changed
  # in any way, then read it.  If the file is now gone and we have an
  # open file descriptor for it, then read to the end of it and then
  # close it.
  my $file_status = $self->status;
  my $fd          = $open_file_cache->get_fd($fid);
  my $load_data   = $file_status != 0;
  if ($file_status == -1) {
    my $message = "file '$sfile_fids[$fid]' did exist and is now gone.";
    email_message($config_global{warn_email}, $message);
    warn "$0: warning: $message\n";
    unless ($fd) {
      $self->[I_LAST_READ_TIME] = -1;
      return 0;
    }
  }

  # Test if the file was up to date and now is not.  If so, then send
  # a message.  Do not send a message if the file was current in the
  # previous day is now is not current today.
  my $old_is_current     = $self->[I_IS_CURRENT];
  my $old_is_current_day = $self->[I_IS_CURRENT_DAY];
  my $current_day        = (localtime($self->last_stat_time))[3];
  $self->[I_IS_CURRENT]  = $self->is_current;
  if ($old_is_current and
      !$self->[I_IS_CURRENT] and
      ($old_is_current_day == $current_day)) {
    my $message = "file '$sfile_fids[$fid]' was current and now is not.";
    warn "$0: warning: $message\n";
    email_message($config_global{warn_email}, $message);
  }

  # If we don't have to load the data from this file yet, then test to
  # see if the data needs to be loaded if the file modification time
  # is greater than the time at which it was last read.
  my $file_mtime = $self->file_mtime;
  unless ($load_data) {
    $load_data = $file_mtime > $self->[I_LAST_READ_TIME];
  }

  # If the file still does not have to be loaded, now test to see if
  # the timestamp of the last data point is larger than the last time
  # of any RRD files that depend on this source file.
  my $last_data_time = $self->[I_LAST_DATA_TIME];
  unless ($load_data) {
    foreach my $rrd_key (@{$self->[I_MY_RRD_LIST]}) {
      if ($self->[I_ALL_RRD_REF]{$rrd_key}->rrd_update_time < $last_data_time) {
        $load_data = 1;
        last;
      }
    }
  }

  return 0 unless $load_data;

  # Try to get a file descriptor to open the file.  Skip the first
  # line if the first line is used for column descriptions.

  my $opened_new_fd = 0;
  unless ($fd) {
    unless ($fd = $open_file_cache->open($fid, $file_mtime)) {
      warn "$0: warning: cannot open '$sfile_fids[$fid]' for reading: $!\n";
      return 0;
    }
    <$fd> if $self->[I_FIRST_LINE];
    $opened_new_fd = 1;
  }

  my $date_column_index = $self->[I_DATE_COLUMN_INDEX];
  my $use_file_mtime    = $self->[I_DATE_SOURCE][0] eq 'file_mtime';
  my $number_added      = 0;
  my $close_once_done   = 0;
  my $number_columns    = @{$self->[I_COLUMN_DESCRIPTION]};

  # Get the filename if the measurement time is loaded from the file
  # instead of from the last modified time and the time should be
  # parsed using the date_parse subroutine.
  my $date_parse = $self->[I_DATE_PARSE];
  my $filename;
  if (!$use_file_mtime and $date_parse) {
    $filename = $sfile_fids[$self->fid];
  }

  # Load in all of the data possible and send it to each plot.
  while (defined(my $line = <$fd>)) {
    # Skip the line if the word timestamp appears in it.  This is a
    # temporary fix for orcallator.se to place a new information line
    # in the output file when it starts up.
    next if $line =~ /timestamp/;

    my @line = split(' ', $line);

    # Skip this input line if 1) the file uses the first line to
    # define the column names, 2) the number of columns loaded is not
    # equal to the number of columns in the column description.
    if ($self->[I_FIRST_LINE] and @line != $number_columns) {
      warn "$0: number of columns in line $. of '$sfile_fids[$fid]' does not ",
           "match column description.\n";
      next;
    }

    my $time;
    if ($use_file_mtime) {
      $time = $self->file_mtime;
    } elsif ($filename) {
      $time = &$date_parse($filename, $line[$date_column_index]);
    } else {
      $time = $line[$date_column_index];
    }
    $last_data_time = $time if $time > $last_data_time;

    # If the file status from the source data file is greater than
    # zero, then it means the file has changed in some way, so we need
    # to do updates for all plots.  Load the available data, calculate
    # the value that needs to go to each RRD and push the value to the
    # RRD.
    my $add    = 0;
    my %values = &{$self->[I_CHOOSE_DATA_SUB]}(@line);
    foreach my $rrd_key (@{$self->[I_MY_RRD_LIST]}) {
      my $value = $values{$rrd_key};
      if (defined $value) {
        if ($self->[I_ALL_RRD_REF]{$rrd_key}->queue_data($time, $value)) {
          if ($opt_verbose > 2 and !$add) {
            print "  Loaded '@line' at ", scalar localtime($time),
                  " ($time).\n";
          }
          $add = 1;
        }
      } else {
        $close_once_done = 1;
        warn "$0: internal error: expecting RRD name '$rrd_key' but no data ",
             "loaded from '", $self->filename, "' at time ",
             scalar localtime($time), " ($time).\n";
      }
    }
    ++$number_added if $add;
  }

  # Update the time when the file was last read.
  $self->[I_LAST_READ_TIME] = time;
  $self->[I_LAST_DATA_TIME] = $last_data_time;

  $open_file_cache->change_weight($fid, $file_mtime);

  # Now two special cases to handle.  First, if the file was removed
  # and we had an open file descriptor to it, then close the file
  # descriptor.  Second, if the file has a new device number or inode
  # and we had a already opened file descriptor to the file, then
  # close the descriptor, reopen it and read all the rest of the data.
  # If neither of these cases is true, then close the file if the file
  # should be reopened next time.
  if ($file_status == 2 and !$opened_new_fd) {
    $open_file_cache->close($fid) or
      warn "$0: warning: cannot close '$sfile_fids[$fid]' for reading: $!\n";
    # Setting the last_read_time to -1 will force load_new_data to
    # read it.
    $self->[I_LAST_READ_TIME] = -1;
    $number_added += $self->load_new_data;
  } elsif ($file_status == -1 or
           $close_once_done   or
           $self->[I_REOPEN]  or
           $open_file_cache->is_pipe($fid)) {
    $open_file_cache->close($fid) or
      warn "$0: warning: cannot close '$sfile_fids[$fid]' for reading: $!\n";
  }

  $number_added;
}

sub rrds {
  @{$_[0]->[I_MY_RRD_LIST]};
}

sub filename {
  $sfile_fids[$_[0]->fid];
}

1;
