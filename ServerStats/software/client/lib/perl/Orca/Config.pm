# Orca::Config: Manage configuration parameters for Orca.
#
# $HeadURL: file:///var/www/svn/repositories-public/orcaware-public/orca/trunk/lib/Orca/Config.pm $
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

package Orca::Config;

use strict;
use Carp;
use Exporter;

use Orca::Constants     qw($opt_verbose
                           $is_sub_re
                           die_when_called
                           $ORCA_VER_MAJOR
                           $ORCA_VER_MINOR
                           $ORCA_VER_PATCH
                           $ORCA_VER_QUOTED
                           @CONST_IMAGE_PLOT_TYPES
                           %CONST_IMAGE_PLOT_INFO
                           @IMAGE_PLOT_TYPES
                           @IMAGE_PDP_COUNTS
                           @IMAGE_TIME_SPAN
                           $MAX_PLOT_TYPE_LENGTH
                           $INCORRECT_NUMBER_OF_ARGS);
use Orca::SourceFileIDs qw(@sfile_fids);
use vars qw(@EXPORT_OK @ISA $VERSION);

@ISA     = qw(Exporter);
$VERSION = (substr q$Revision: 513 $, 10)/100.0;

# Export the main subroutine to load configuration data and a subroutine
# to get a color indexed by an integer.
push(@EXPORT_OK, qw(data_index_to_color load_config));

# The following array and hashes hold the contents of the
# configuration file.
use vars         qw(%config_global
                    @config_groups
                    @config_groups_names
                    @config_plots);
push(@EXPORT_OK, qw(%config_global
                    @config_groups
                    @config_groups_names
                    @config_plots));

# This is a list of global parameters that control which plots
# (i.e. monthly, yearly) are created.
my $pre_plot_type  = 'generate_';
my $post_plot_type = '_plot';
my @plot_type_global_elements = map { "$pre_plot_type$_$post_plot_type" }
                                @CONST_IMAGE_PLOT_TYPES;

# The pcl_* variables are used to read the configuration file and how
# to treat each configuration file parameter.

# These are state variables are used for reading the config file.  The
# variables pcl_group_index and pcl_plot_index are strings that
# represent a number that is used as an index into @config_groups and
# @config_plots respectively.  If the string is negative, including
# -0, then the configuration is not being defined, otherwise it holds
# the index into the appropriate array that is being defined.
my $pcl_group_index = '-0';
my $pcl_plot_index  = '-0';
my $pcl_group_name  = '';

# This keeps track of group names that have been loaded.
my %pcl_group_name_to_index;

# The @pcl_X_elements are the list of valid options for the global,
# group and plot sections of the configuration file.
my %pcl_global_elements        =   (base_dir            => 1,
                                    expire_images       => 1,
                                    find_times          => 1,
                                    html_dir            => 1,
                                    html_page_footer    => 1,
                                    html_page_header    => 1,
                                    html_top_title      => 1,
                                    late_interval       => 1,
                                    max_filename_length => 1,
                                    require             => 1,
                                    rrd_dir             => 1,
                                    state_file          => 1,
                                    warn_email          => 1);
map { $pcl_global_elements{$_} = 1 } @plot_type_global_elements;
my %pcl_group_elements         =   (column_description  => 1,
                                    date_parse          => 1,
                                    date_source         => 1,
                                    filename_compare    => 1,
                                    find_files          => 1,
                                    interval            => 1,
                                    late_interval       => 1,
                                    reopen              => 1);
my %pcl_plot_elements          =   (base                => 1,
                                    color               => 1,
                                    data                => 1,
                                    data_min            => 1,
                                    data_max            => 1,
                                    data_type           => 1,
                                    flush_regexps       => 1,
                                    href                => 1,
                                    hrule               => 1,
                                    legend              => 1,
                                    line_type           => 1,
                                    logarithmic         => 1,
                                    plot_height         => 1,
                                    plot_min            => 1,
                                    plot_max            => 1,
                                    plot_width          => 1,
                                    required            => 1,
                                    rigid_min_max       => 1,
                                    source              => 1,
                                    summary_format      => 1,
                                    title               => 1,
                                    y_legend            => 1);

# %pcl_group_append_elements and %pcl_plot_append_elements define
# those parameters that generate a list of values and every appearance
# of one in the configuration file appends the value to the array.  If
# an entry is added to %pcl_plot_append_elements, make sure to update
# Orca::SourceFile::add_plots.
my %pcl_group_append_elements  =   ();
my %pcl_plot_append_elements   =   (color               => 1,
                                    data                => 1,
                                    data_min            => 1,
                                    data_max            => 1,
                                    data_type           => 1,
                                    hrule               => 1,
                                    legend              => 1,
                                    line_type           => 1,
                                    summary_format      => 1);

# This is a list of parameters that need their paths cleaned up.
my %pcl_filepath_elements      =   (find_files          => 1,
                                    html_dir            => 1,
                                    rrd_dir             => 1,
                                    state_file          => 1);

# This is a list of parameters that do not require an argument and
# when there is no argument for the parameter, the value is set to
# true.
my %pcl_no_arg_elements        =   (flush_regexps       => 1,
                                    logarithmic         => 1,
                                    required            => 1,
                                    rigid_min_max       => 1);

# These are a list of parameters that keep all of the arguments to the
# parameter, not just the first one.  Internally, the parameter value
# is stored as a reference to an array.
my %pcl_global_keep_as_array   =   ('require'           => 1);
my %pcl_group_keep_as_array    =   (column_description  => 1,
                                    date_source         => 1,
                                    find_files          => 1);
my %pcl_plot_keep_as_array     =   (data                => 1);

# The following variables are used to check that the configuration
# file contains the required parameters and that the parameters are
# set to the correct values.  The @cc_required_* are the names of the
# parameters that must occur in a configuration file.
my @cc_required_global         = qw(html_dir
                                    rrd_dir
                                    state_file);
my @cc_required_group          = qw(column_description
                                    date_source
                                    find_files
                                    interval);
my @cc_required_plot           = qw(data
                                    source);

# The parameters listed in @cc_default_is_true_* are set to 1 if they
# are not set in the configuration file.
my @cc_default_is_true_global  =   @plot_type_global_elements;
my @cc_default_is_true_group   =   ();
my @cc_default_is_true_plot    =   ();

# The parameters listed in @cc_default_is_false_* are set to '' if
# they are not set in the configuration file.
my @cc_default_is_false_global = qw(expire_images
                                    find_times
                                    html_page_footer
                                    html_page_header
                                    html_top_title
                                    late_interval
                                    warn_email);
my @cc_default_is_false_group  = qw(date_parse
                                    reopen);
my @cc_default_is_false_plot   = qw(flush_regexps
                                    href
                                    late_interval
                                    plot_width
                                    plot_height);

# These parameters are set to true if they do not appear in the
# configuration file.
my %pcl_global_default_is_true = map { ($_, 1) } @plot_type_global_elements;
my %pcl_group_default_is_true  =   ();
my %pcl_plot_default_is_true   =   ();


# This is the default list of colors.
my @cc_default_colors          =   ('00ff00',   # Green
                                    '0000ff',   # Blue
                                    'ff0000',   # Red
                                    'a020f0',   # Magenta
                                    'ffa500',   # Orange
                                    'a52a2a',   # Brown
                                    '00ffff',   # Cyan
                                    '00aa00',   # Dark Green
                                    'eeee00',   # Yellow
                                    '707070',   # Dark Gray
                                    'be711d',   # Rust 11
                                    'dad1ff',   # Lilas
                                    '7df5cb',   # Biz green
                                    'ff81a9',   # Pink
                                    'ffe114',   # Golden
                                    '96a125',   # Olive
                                    'ffd8ae',   # Peaches
                                    'bebebe',   # Light Grey
                                    'ebeec3',   # Taupe
                                    '860033',   # Bourgogne
                                    '19a48a',   # Ocean green
                                    'b8a390',   # VLB
                                    'a3c5a6',   # Blackboard green
                                    'ffd2b2',   # Light orange
                                    '000000',   # Black
                                    'fff8bd',   # Post-it (tm) Yellow
                                    'c7eaff',   # Ice blue
                                    'd3ff52');  # Gatorade green

sub data_index_to_color {
  $cc_default_colors[$_[0] % @cc_default_colors];
}

# This variable stores the anonymous subroutine that compares FIDs
# when a group in the configuration files does not contain a
# filename_compare parameter.
my $cmp_fids_sub;

# This subroutine takes a string and compiles it into a subroutine.
sub compile_sub {
  unless (@_ == 4) {
    confess "$0: Orca::Config::compile_sub $INCORRECT_NUMBER_OF_ARGS";
  }

  my ($option, $where, $config_filename, $expr) = @_;

  $expr = "sub { $expr }" if $expr !~ /$is_sub_re/o;

  my $sub;
  {
    local $SIG{__DIE__}  = 'DEFAULT';
    local $SIG{__WARN__} = \&die_when_called;
    $sub = eval $expr;
  }

  if ($@) {
    warn "$0: cannot evalulate '$option' in $where in ",
         "'$config_filename':\n   $expr\nOutput: $@\n";
    return;
  } else {
    return $sub;
  }
}

# This subroutine takes an expression and creates an anonymous
# subroutine that calculates the late interval.
sub compile_late_interval {
  unless (@_ == 3) {
    confess "$0: Orca::Config::compile_late_interval $INCORRECT_NUMBER_OF_ARGS";
  }

  my ($where, $config_filename, $expr) = @_;

  $expr =~ s/\binterval\b/\$_[0]/g;
  my $sub = compile_sub('late_interval',
                        $where,
                        $config_filename,
                        $expr);
  return unless $sub;

  local $SIG{__DIE__}  = 'DEFAULT';
  local $SIG{__WARN__} = \&die_when_called;
  eval '&$sub(3.1415926) + 0;';
  if ($@) {
    warn "$0: cannot execute 'late_interval' in $where in ",
         "'$config_filename':\n   $expr\nOutput: $@\n";
    return;
  } else {
    return $sub;
  }
}

# This subroutine takes an array reference, a list of number of
# elements that should be in the array, and the default value to use
# if there are no set values.  For the array elements that are not
# set, use the last set value.
sub fill_append_elements {
  unless (@_ == 3) {
    confess "Orca::Config::fill_append_elements $INCORRECT_NUMBER_OF_ARGS";
  }

  my ($array_ref, $number_datas, $default_value) = @_;

  unless (defined $array_ref->[0]) {
    $array_ref->[0] = $default_value;
  }
  for (my $k=1; $k<$number_datas; ++$k) {
    unless (defined $array_ref->[$k]) {
      $array_ref->[$k] = $array_ref->[$k-1];
    }
  }
}

sub check_config {
  unless (@_ == 1) {
    confess "$0: Orca::Config::check_config $INCORRECT_NUMBER_OF_ARGS";
  }

  my $config_filename = shift;

  # This counter is incremented for each error in the configuration
  # file.
  my $number_errors = 0;

  # Check that the required version of Orca is being used.
  if (defined $config_global{require}) {
    my @require = @{$config_global{require}};
    if (@require == 2) {
      my ($require_what, $required_version) = @require;
      if ($require_what eq 'Orca') {
        # Split the required Orca version string on periods and
        # compare each element in an array created from the split
        # string with an array created from the Orca version numbers.
        my @required_version = split(/\./, $required_version);

        # Check each substring.  If it is not defined or has 0 length
        # or is not an integer number, then set it to 0 and complain.
        my $warned = 0;
        for (my $i=0; $i<@required_version; ++$i) {
          unless (defined $required_version[$i] and
                  length $required_version[$i] and
                  $required_version[$i] =~ /^\d+$/) {
            unless ($warned) {
              warn "$0: error: 'require Orca $required_version' has an ",
                   "illegally formatted version string in ",
                   "'$config_filename'.\n";
              $warned = 1;
            }
            ++$number_errors;
            $required_version[$i] = 0;
          }
        }

        # The Orca version number has three elements, so to have a
        # good comparison, ensure that the required version number
        # array has at least three elements.
        for (my $i=@required_version; $i<3; ++$i) {
          $required_version[$i] = 0;
        }

        # If the required version string has more elements than the
        # Orca version array, then extend the Orca version array.
        my @orca_version = ($ORCA_VER_MAJOR, $ORCA_VER_MINOR, $ORCA_VER_PATCH);
        for (my $i=@orca_version; $i<@required_version; ++$i) {
          $orca_version[$i] = 0;
        }

        my $orca_version_ok = 1;
        for (my $i=0; $i<@orca_version; ++$i) {
          if ($orca_version[$i] < $required_version[$i]) {
            $orca_version_ok = 0;
            last;
          }
        }

        unless ($orca_version_ok) {
          warn "$0: Orca version $ORCA_VER_QUOTED is less than the required ",
               "version $required_version specified in '$config_filename'.\n";
          ++$number_errors;
        }
      } else {
        warn "$0: error: 'require' only accepts 'Orca' as first argument in ",
             "'$config_filename'.\n";
        ++$number_errors;
      }
    } else {
      warn "$0: error: 'require' needs two arguments in '$config_filename'.\n";
      ++$number_errors;
    }
  }

  # If rrd_dir is not set, then use base_dir.  Only warn if both are
  # not set.
  unless (defined $config_global{rrd_dir}) {
    if (defined $config_global{base_dir}) {
      $config_global{rrd_dir} = $config_global{base_dir};
    } else {
      warn "$0: error: must set 'rrd_dir' in '$config_filename'.\n";
      ++$number_errors;
    }
  }

  # Check that we the required options are satisfied.
  my $required_error = 0;
  foreach my $option (@cc_required_global) {
    unless (defined $config_global{$option}) {
      warn "$0: error: must set '$option' in '$config_filename'.\n";
      $required_error = 1;
      ++$number_errors;
    }
  }

  # Exit now if there were any required options that were not set
  # since use of then will cause uninitialized warnings.
  if ($required_error) {
    return $number_errors;
  }

  # Check if the html_dir and rrd_dir directories exist.
  foreach my $dir_key ('html_dir', 'rrd_dir') {
    my $dir = $config_global{$dir_key};
    unless (-d $dir) {
      warn "$0: error: please create $dir_key '$dir'.\n";
      ++$number_errors;
    }
  }

  # Having a single directory used for the html_dir and the rrd_dir is
  # not a supported configuration.
  if ($config_global{html_dir} eq $config_global{rrd_dir}) {
    my $dir = $config_global{html_dir};
    warn "$0: error: 'html_dir' and 'rrd_dir' '$dir' are identical.\n";
    ++$number_errors;
  }

  # Set any optional global parameters to '' if it isn't defined in
  # the configuration file.
  foreach my $option (@cc_default_is_false_global) {
    $config_global{$option} = '' unless defined $config_global{$option};
  }

  # Set any optional global parameters to 1 if it isn't defined in the
  # configuration file.
  foreach my $option (@cc_default_is_true_global) {
    $config_global{$option} = 1 unless defined $config_global{$option};
  }

  # Set the max_filename_length if it is not set and check it
  # otherwise.
  my $mfl = $config_global{max_filename_length};
  if (defined $mfl) {
    unless ($mfl =~ /^\d+$/ and $mfl > 63) {
      warn "$0: error: max_filename_length '$mfl' is not a number > 63.\n";
      ++$number_errors;
    }
  } else {
    $config_global{max_filename_length} = 235;
  }

  # Late_interval is a valid mathematical expression. Replace the word
  # interval with $_[0].  Try the subroutine to make sure it works.
  unless ($config_global{late_interval}) {
    $config_global{late_interval} = 'interval';
  }
  my $global_late_interval_expr = $config_global{late_interval};
  my $sub = compile_late_interval('global section',
                                  $config_filename,
                                  $config_global{late_interval});
  if ($sub) {
    $config_global{late_interval} = $sub;
  } else {
    ++$number_errors;
  }

  # Convert the list of find_times into an array of fractional hours.
  my @find_times;
  foreach my $find_time (split(' ', $config_global{find_times})) {
    if (my ($hours, $minutes) = $find_time =~ /^(\d{1,2}):(\d{2})/) {
      # Because of the regular expression match we're doing, the hours
      # and minutes will only be positive, so check for hours > 23 and
      # minutes > 59.
      unless ($hours < 24) {
        warn "$0: warning: ignoring find_times '$find_time': hours must be ",
             "less than 24.\n";
        ++$number_errors;
        next;
      }
      unless ($minutes < 60) {
        warn "$0: warning: ignoring find_times '$find_time': minutes must be ",
             "less than 60.\n";
        ++$number_errors;
        next;
      }
      push(@find_times, $hours + $minutes/60.0);
    } else {
      warn "$0: warning: ignoring find_times '$find_time': illegal format.\n";
      ++$number_errors;
    }
  }
  $config_global{find_times} = [ sort { $a <=> $b } @find_times ];

  # Using the parameters in the configuration file, generate the list
  # of plots to create.
  @IMAGE_PLOT_TYPES = ();
  @IMAGE_PDP_COUNTS = ();
  @IMAGE_TIME_SPAN  = ();
  $MAX_PLOT_TYPE_LENGTH = 0;
  foreach my $type (@CONST_IMAGE_PLOT_TYPES) {
    if ($config_global{"$pre_plot_type$type$post_plot_type"}) {
      my $data_ref = $CONST_IMAGE_PLOT_INFO{$type};
      unless ($data_ref) {
        confess "$0: internal error: \$CONST_IMAGE_PLOT_INFO{$type} is ",
                "undefined.\n";
      }
      push(@IMAGE_PLOT_TYPES, $type);
      push(@IMAGE_PDP_COUNTS, $data_ref->[0]);
      push(@IMAGE_TIME_SPAN,  $data_ref->[1]);
      my $type_length = length($type);
      if ($type_length > $MAX_PLOT_TYPE_LENGTH) {
        $MAX_PLOT_TYPE_LENGTH = $type_length;
      }
    }
  }

  # There must be at least one timespan plot.
  unless (@IMAGE_PLOT_TYPES) {
    warn "$0: error: generate_*_plots parameters turn off all plots in ",
         "'$config_filename'.\n";
    ++$number_errors;
  }

  # There must be at least one group.
  unless (@config_groups) {
    warn "$0: error: must define at least one 'group' in ",
         "'$config_filename'.\n";
    ++$number_errors;
  }

  # For each group parameter there are required options.
  for (my $i=0; $i<@config_groups; ++$i) {
    my $group      = $config_groups[$i];
    my $group_name = $config_groups_names[$i];

    $required_error = 0;
    foreach my $option (@cc_required_group) {
      unless (defined $group->{$option}) {
        warn "$0: error: must set '$option' for 'group $group_name' ",
             "in '$config_filename'.\n";
        $required_error = 1;
        ++$number_errors;
      }
    }

    # Do not continue checking this group if there were any required
    # options that were not set since use of then will cause
    # uninitialized warnings from Perl later on.
    next if $required_error;

    # Set any optional group parameters to '' if it isn't defined in
    # the configuration file.
    foreach my $option (@cc_default_is_false_group) {
      $group->{$option} = '' unless defined $group->{$option};
    }

    # Set any optional group parameters to 1 if it isn't defined in
    # the configuration file.
    foreach my $option (@cc_default_is_true_group) {
      $group->{$option} = 1 unless defined $group->{$option};
    }

    # Check that the interval is a number.
    unless ($group->{interval} =~ /^\d+$/ and $group->{interval} > 0) {
      warn "$0: error: interval '$group->{interval}' for 'group $group_name' ",
           "is not an integer greater than 0 in '$config_filename'.\n";
      ++$number_errors;
    }

    # Check the late_interval.  If it does not exist, then use the
    # global one.
    my $expr;
    if ($expr = $group->{late_interval}) {
      $sub = compile_late_interval("'group $group_name'",
                                   $config_filename,
                                   $expr);
      if ($sub) {
        $group->{late_interval} = $sub;
      } else {
        ++$number_errors;
      }
    } else {
      $expr = $global_late_interval_expr;
      $group->{late_interval} = $config_global{late_interval};
    }
    {
      local $SIG{__DIE__}  = 'DEFAULT';
      local $SIG{__WARN__} = \&die_when_called;
      $sub = $group->{late_interval};
      my $value;
      eval '$value = &$sub($group->{interval});';
      if ($@) {
        warn "$0: cannot execute 'late_interval' in 'group $group_name' in ",
             "'$config_filename':\n   $expr\nOutput: $@\n";
        ++$number_errors;
      } elsif ($value !~ /^\d+$/ and $value <= 0) {
        warn "$0: 'late_interval' in 'group $group_name' did not generate an ",
             "integer '$value' greater than 0.\n";
        ++$number_errors;
      }
      $group->{late_interval} = $value;
    }

    # There are three intervals associated with each file.  The first
    # is the data update interval.  This is the same interval used to
    # generate the RRDs.  The second interval is the interval before
    # the file is considered late and is larger than the data update
    # interval.  This interval is calculated by using the mathematical
    # expression given in the 'late_interval' configuration option.
    # If 'late_interval' is not defined, then it gets defaulted to the
    # data update interval.  The last interval is the interval to use
    # to tell the program when to attempt to read the file next.
    # Because it can take some time for the source files to be
    # updated, we don't want to read the file immediately after the
    # data update interval is done.  For this reason, choose a read
    # interval that is somewhere in between the data source interval
    # and the late_interval.  Use the multiplicative average of the
    # data update interval and the late interval since the resulting
    # value is closer to the data update interval.  Ie:
    # (20 + 5)/2 = 12.5.  Sqrt(20*5) = 10.
    $group->{read_interval} = sqrt($group->{interval}*$group->{late_interval});

    # Create the filename comparison function.  The function must be
    # handle input ala sort() via the package global $a and $b variables.
    if ($group->{filename_compare} or !$cmp_fids_sub) {
      $expr = $group->{filename_compare} ?
              $group->{filename_compare} :
              'sub { $a cmp $b }';
      if (compile_sub('filename_compare',
                      "'group $group_name'",
                      $config_filename,
                      $expr)) {
        # This subroutine looks fine.  Now change all the variables to
        # use file IDs instead.
        $expr =~ s/\$a(\W)/\$sfile_fids[\$a]$1/g;
        $expr =~ s/\$b(\W)/\$sfile_fids[\$b]$1/g;
        $sub  = compile_sub('filename_compare',
                            "group '$group_name'",
                            $config_filename,
                            $expr);
        if ($sub) {
          $cmp_fids_sub = $sub if !$group->{filename_compare};
          $group->{filename_compare} = $sub;
        } else {
          ++$number_errors;
        }
      } else {
        ++$number_errors;
      }
    } else {
      $group->{filename_compare} = $cmp_fids_sub;
    }

    # Check that the date_source is either column_name followed by a
    # column name or file_mtime for the file modification time.  If a
    # column_name is used, then compile the data_parse subroutine if
    # it exists.
    my $date_source = $group->{date_source}[0];
    $group->{date_parse} = 0;
    if ($date_source eq 'column_name') {
      if (@{$group->{date_source}} != 2) {
        warn "$0: error: incorrect number of arguments for 'date_source' for ",
             "'group $group_name'.\n";
        ++$number_errors;
      } elsif (my $expr = $group->{date_parse}) {
        unless ($group->{date_parse} = compile_sub('date_parse',
                                                   "group '$group_name'",
                                                   $config_filename,
                                                   $expr)) {
          ++$number_errors;
        }
      }
    } else {
      unless ($date_source eq 'file_mtime') {
        warn "$0: error: illegal argument for 'date_source' for ",
             "'group $group_name'.\n";
        ++$number_errors;
      }
    }
    $group->{date_source}[0] = $date_source;

    # Validate the regular expression for find_files and get a unique
    # list of them.  Check if the regular expressions contain any ()'s
    # that will place the found files into different groups.  If any
    # ()'s are found, then the output HTML and image tree will use
    # subdirectories for each group.
    #
    # In this code comment, all path names are Perl escaped, so the
    # directory . would be written as \. instead.
    #
    # Since we do not want to search on the current directory, find
    # any find_files' that begin a regular expression with a \./ and
    # remove it.  Also remove any matches for /\./ in the path since
    # they are unnecessary.  However, do not remove searches for /./,
    # since this can match single character files or directories.
    my %find_files;
    my $find_files = $group->{find_files};
    my $number_finds = @$find_files;
    for (my $j=0; $j<$number_finds; ++$j) {
      my $orig_find        = $find_files->[$j];
      my $find             = $orig_find;
      $find                =~ s:^\\\./+::;
      $find                =~ s:/+\\\./+:/:g;
      $find                = $orig_find unless $find;
      $find_files->[$j]    = $find;
      my $test_string      = 'abcdefg';
      local $SIG{__DIE__}  = 'DEFAULT';
      local $SIG{__WARN__} = \&die_when_called;
      eval { $test_string =~ /$find/ };
      if ($@) {
        warn "$0: error: illegal regular expression in 'find_files ",
             "$orig_find' for 'files $group_name' in ",
             "'$config_filename':\n$@\n";
        ++$number_errors;
      } else {
        $find_files{$find} = 1;
      }
    }
    $group->{find_files} = [sort keys %find_files];
  }

  # There must be at least one plot.
  unless (@config_plots) {
    warn "$0: error: must define at least one 'plot' in '$config_filename'.\n";
    ++$number_errors;
  }

  # Foreach plot there are required options.  Create default options
  # if the user has not done so.
  for (my $i=0; $i<@config_plots; ++$i) {
    my $plot = $config_plots[$i];

    my $j = $i + 1;
    $required_error = 0;
    foreach my $option (@cc_required_plot) {
      unless (defined $plot->{$option}) {
        $required_error = 1;
        warn "$0: error: must set '$option' for 'plot' #$j in ",
             "'$config_filename'.\n";
        ++$number_errors;
      }
    }

    # Do not continue checking this plot if there were any required
    # options that were not set since use of then will cause
    # uninitialized warnings from Perl later on.
    next if $required_error;

    # Create an array for each plot that will have a list of images that
    # were generated from this plot.
    $plot->{created_orca_images} = [];

    # Set any optional plot parameters to '' if it isn't defined in
    # the configuration file.
    foreach my $option (@cc_default_is_false_plot) {
      $plot->{$option} = '' unless defined $plot->{$option};
    }

    # Set any optional plot parameters to 1 if it isn't defined in
    # the configuration file.
    foreach my $option (@cc_default_is_true_plot) {
      $plot->{$option} = 1 unless defined $plot->{$option};
    }

    # Set the default plot width and height.
    $plot->{plot_width}  =  500 unless $plot->{plot_width};
    $plot->{plot_height} =  125 unless $plot->{plot_height};

    # Make sure the base is either 1000 or 1024.
    if (defined $plot->{base} && length($plot->{base})) {
      if ($plot->{base} != 1000 and $plot->{base} != 1024) {
        warn "$0: error: plot #$j must set base to be either 1000 or 1024.\n";
        ++$number_errors;
      }
    } else {
      $plot->{base} = 1000;
    }

    # Get the number of data's in this plot.
    my $number_datas = @{$plot->{data}};

    # If the data_min and data_max are not set, then set it to U.  Use
    # the last set data_min and data_max for those that are not set.
    $plot->{data_min} = [] unless defined $plot->{data_min};
    $plot->{data_max} = [] unless defined $plot->{data_max};
    fill_append_elements($plot->{data_min}, $number_datas, 'U');
    fill_append_elements($plot->{data_max}, $number_datas, 'U');

    # The data type must be either gauge, absolute, or counter.
    $plot->{data_type} = [] unless defined $plot->{data_type};
    for (my $k=0; $k<@{$plot->{data_type}}; ++$k) {
      my $data_type  = $plot->{data_type}[$k];
      my $first_char = lc(substr($data_type, 0, 1));
      if ($first_char eq 'g') {
        $data_type = 'GAUGE';
      } elsif ($first_char eq 'c') {
        $data_type = 'COUNTER';
      } elsif ($first_char eq 'a') {
        $data_type = 'ABSOLUTE';
      } elsif ($first_char eq 'd') {
        $data_type = 'DERIVE';
      } else {
        $data_type = 'GAUGE';
        my $l      = $k + 1;
        warn "$0: error: 'plot' #$j 'data_type #$l '$data_type' in ",
             "'$config_filename' must be gauge, counter, derive, or ",
             "absolute.\n";
        ++$number_errors;
      }
      $plot->{data_type}[$k] = $data_type;
    }
    fill_append_elements($plot->{data_type}, $number_datas, 'GAUGE');

    # The data source needs to be a valid group name.  Replace the
    # group's name with its index.
    my $source = delete $plot->{source};
    unless (defined $source) {
      warn "$0: error: plot #$j 'source $source' requires one group_name ",
           "argument in '$config_filename'.\n";
      ++$number_errors;
      next;
    }
    my $source_index = $pcl_group_name_to_index{$source};
    unless (defined $source_index) {
      warn "$0: error: plot #$j 'source $source' references non-existant ",
           "'group' in '$config_filename'.\n";
      ++$number_errors;
      next;
    }
    $plot->{source_index} = $source_index;

    # Set the legends of any columns not defined.
    $plot->{legend} = [] unless defined $plot->{legend};
    for (my $k=@{$plot->{legend}}; $k<$number_datas; ++$k) {
      $plot->{legend}[$k] = "@{$plot->{data}[$k]}";
    }

    # If the generic y_legend is not set, then set it equal to the
    # first legend.
    unless (defined $plot->{y_legend}) {
      $plot->{y_legend} = $plot->{legend}[0];
    }

    # Set the colors of any data's not defined.
    $plot->{color} = [] unless defined $plot->{color};
    for (my $k=@{$plot->{color}}; $k<$number_datas; ++$k) {
      $plot->{color}[$k] = data_index_to_color($k);
    }

    # Check each line type setting.  Use the last line_type to set any
    # following line_type's if they are not specified.
    $plot->{line_type} = [] unless defined $plot->{line_type};
    for (my $k=0; $k<@{$plot->{line_type}}; ++$k) {
      my $line_type = $plot->{line_type}[$k];
      if ($line_type =~ /^line([123])$/i) {
        $line_type = "LINE$1";
      } elsif ($line_type =~ /^area$/i) {
        $line_type = 'AREA';
      } elsif ($line_type =~ /^stack$/i) {
        $line_type = 'STACK';
      } else {
        $line_type = 'LINE1';
        my $l      = $k + 1;
        warn "$0: error: 'plot' #$j illegal 'line_type' #$l '$line_type'.\n";
        ++$number_errors;
      }
      $plot->{line_type}[$k] = $line_type;
    }
    fill_append_elements($plot->{line_type}, $number_datas, 'LINE1');

    # If the summary_format is not set, then set it to a reasonable
    # default.  Use the last set summary_format for those that are not
    # set.
    $plot->{summary_format} = [] unless defined $plot->{summary_format};
    fill_append_elements($plot->{summary_format}, $number_datas, '%9.3lf %S');

    # If the title is not set, then set it equal to all of the legends
    # with the group name prepended.
    unless (defined $plot->{title}) {
      my $title = '%G ';
      for (my $k=0; $k<$number_datas; ++$k) {
        $title .= $plot->{legend}[$k];
        $title .= " & " if $k < $number_datas-1;
      }
      $plot->{title} = $title;
    }

    # The hrule array reference must exist.
    $plot->{hrule} = [] unless defined $plot->{hrule}
  }

  $number_errors;
}

sub _trim_path {
  my $path = shift;

  # Replace any multiple /'s with a single /.
  $path =~ s:/{2,}:/:g;

  # Trim any trailing /.'s unless the path is only /., in which case
  # make it /.
  if ($path eq '/.') {
    $path = '/';
  } else {
    $path =~ s:/\.$::;
  }
  $path;
}

# Go through each input line separately and keep a state of the type
# of object being processed between global, group and plot options.
sub process_config_line {
  my ($config_filename, $line_number, $line) = @_;

  # This counter is incremented for each error in the configuration
  # file.
  my $number_errors = 0;

  # Take the line and split it and make the first element lowercase.
  my @line = split(' ', $line);
  my $key  = lc(shift(@line));

  # Warn if there is no option and it requires an option.  Turn on
  # options that do not require an option argument and do not supply
  # one.
  if ($key ne '}') {
    if ($pcl_no_arg_elements{$key}) {
      push(@line, 1) unless @line;
    } else {
      unless (@line) {
        warn "$0: warning: option '$key' needs arguments in ",
             "'$config_filename' line $line_number.\n";
        ++$number_errors;
        return $number_errors;
      }
    }
  }

  # If the option is a file path option, then clean up paths in the
  # following order:
  # 1) Trim the path.
  # 2) Prepend the base_dir to paths that are not prepended by
  #    ^\\?\.{0,2}/, which matches /, ./, ../, and \./.
  # 3) Trim the resulting path.
  if ($pcl_filepath_elements{$key}) {
    my $base_dir = defined $config_global{base_dir} ?
                  _trim_path($config_global{base_dir}) :
                  '';
    for (my $i=0; $i<@line; ++$i) {
      my $path = _trim_path($line[$i]);
      if ($base_dir) {
        $path = "$base_dir/$path" unless $path =~ m:^\\?\.{0,2}/:;
      }
      $line[$i] = _trim_path($path);
    }
  }

  my $value = "@line";

  # Now check if a group or plot is being processed by examining the
  # state variables.
  my $index_ref;
  my $config_ref;
  my $pcl_elements_ref;
  my $pcl_keep_as_array_ref;
  my $pcl_append_elements_ref;
  my $label;
  if (substr($pcl_group_index, 0, 1) ne '-') {
    $index_ref               = \$pcl_group_index;
    $config_ref              = \@config_groups;
    $pcl_elements_ref        = \%pcl_group_elements;
    $pcl_keep_as_array_ref   = \%pcl_group_keep_as_array;
    $pcl_append_elements_ref = \%pcl_group_append_elements;
    $label                   = "group '$pcl_group_name'";
  } elsif (substr($pcl_plot_index, 0, 1) ne '-') {
    $index_ref               = \$pcl_plot_index;
    $config_ref              = \@config_plots;
    $pcl_elements_ref        = \%pcl_plot_elements;
    $pcl_keep_as_array_ref   = \%pcl_plot_keep_as_array;
    $pcl_append_elements_ref = \%pcl_plot_append_elements;
    $label                   = "plot #$pcl_plot_index";
  }

  # At this point a group or plot is being read.
  if ($index_ref) {
    if ($key eq '}') {
      ++$$index_ref;
      $$index_ref = "-$$index_ref";
      return $number_errors;
    }

    unless ($pcl_elements_ref->{$key}) {
      warn "$0: warning: directive '$key' unknown for $label at line ",
           "$line_number in '$config_filename'.\n";
      ++$number_errors;
      return $number_errors;
    }

    # Handle those elements that can just append.
    if ($pcl_append_elements_ref->{$key}) {
      unless (defined $config_ref->[$$index_ref]{$key}) {
        $config_ref->[$$index_ref]{$key} = [];
      }
      if ($pcl_keep_as_array_ref->{$key}) {
        push(@{$config_plots[$pcl_plot_index]{$key}}, [ @line ]);
      } else {
        push(@{$config_plots[$pcl_plot_index]{$key}}, $value);
      }
      return $number_errors;
    }

    if (defined $config_ref->[$$index_ref]{$key}) {
      warn "$0: warning: '$key' for $label already defined at line ",
           "$line_number in '$config_filename'.\n";
      ++$number_errors;
      return $number_errors;
    }

    if ($pcl_keep_as_array_ref->{$key}) {
      $config_ref->[$$index_ref]{$key} = [ @line ];
    } else {
      $config_ref->[$$index_ref]{$key} = $value;
    }
    return $number_errors;
  }

  # At this point the line is either a global option or the
  # declaration of a group or a plot.  Take care of global parameters.
  if ($pcl_global_elements{$key}) {
    if ($pcl_global_keep_as_array{$key}) {
      $config_global{$key} = [ @line ];
    } else {
      $config_global{$key} = $value;
    }
    return $number_errors;
  }

  # At this point a group or a plot is being defined.
  if ($key eq 'group') {
    unless (@line) {
      warn "$0: error: group needs a group name followed by { at ",
           "line $line_number in '$config_filename'.\n";
      ++$number_errors;
      return $number_errors;
    }
    $pcl_group_index =~ s:^-::;
    $pcl_group_name =  shift(@line);
    unless (@line == 1 and $line[0] eq '{' ) {
      if ($pcl_group_name eq '{') {
        warn "$0: warning: 'group_name {' required after 'group' at ",
             "line $line_number in '$config_filename'.\n";
      } else {
        warn "$0: warning: '{' required after 'group $pcl_group_name' at ",
             "line $line_number in '$config_filename'.\n";
      }
      ++$number_errors;
    }
    if (defined $pcl_group_name_to_index{$pcl_group_name}) {
      warn "$0: warning: 'group $key' at line $line_number in ",
           "'$config_filename' previously defined.\n";
      ++$number_errors;
    }
    $config_groups[$pcl_group_index]{index}      = $pcl_group_index;
    $config_groups_names[$pcl_group_index]       = $pcl_group_name;
    $pcl_group_name_to_index{$pcl_group_name}    = $pcl_group_index;
    return $number_errors;
  }

  # Take care of plots to make.  Include in each plot its index.
  if ($key eq 'plot') {
    $pcl_plot_index =~ s:^-::;
    $config_plots[$pcl_plot_index]{index} = $pcl_plot_index;
    unless (@line == 1 and $line[0] eq '{') {
      $label = "@line";
      $label = " $label" if $label;
      warn "$0: warning: '{' required immediately after plot in 'plot$label' ",
           "at line $line_number in '$config_filename'.\n";
      ++$number_errors;
    }
    return $number_errors;
  }

  warn "$0: warning: unknown directive '$key' at line $line_number in ",
       "'$config_filename'.\n";
  ++$number_errors;

  $number_errors;
}

sub load_config {
  my $config_filename = shift;

  # This counter is incremented for each error in the configuration
  # file.
  my $number_errors = 0;

  unless (open(CONFIG, $config_filename)) {
    warn "$0: error: cannot open '$config_filename' for reading: $!\n";
    ++$number_errors;
    return $number_errors;
  }

  # Load in all lines in the file and then process them.  If a line
  # begins with whitespace, then append it to the previously read line
  # and do not process it.
  my $complete_line = '';
  my $line_number = 1;
  while (<CONFIG>) {
    chomp;
    # Skip lines that begin with #.
    next if /^#/;

    # If the line begins with whitespace, then append it to the
    # previous line.
    if (/^\s+/) {
      $complete_line .= " $_";
      next;
    }

    # Process the previously read complete line.
    if ($complete_line) {
      $number_errors += process_config_line($config_filename,
                                            $line_number,
                                            $complete_line);
    }

    # Now save this read line.
    $complete_line = $_;
    $line_number = $.;
  }

  # If there is any remaining text, then process it as a complete
  # line.
  if ($complete_line) {
    $number_errors += process_config_line($config_filename,
                                          $line_number,
                                          $complete_line);
  }

  close(CONFIG) or
    warn "$0: error in closing '$config_filename': $!\n";

  $number_errors + check_config($config_filename);
}

1;
