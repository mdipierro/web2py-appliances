# Orca::Constants.pm: Global constants for Orca.
#
# $HeadURL: file:///var/www/svn/repositories-public/orcaware-public/orca/trunk/lib/Orca/Constants.pm $
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

package Orca::Constants;

use strict;
use Exporter;
use vars qw(@EXPORT_OK @ISA $VERSION);
@ISA     = qw(Exporter);
$VERSION = (substr q$Revision: 513 $, 10)/100.0;

# ORCA_VER_MAJOR        Orca's major version number.  Increment when
#                       incompatible changes are made to published
#                       interfaces.
# ORCA_VER_MINOR        Orca's minor version number.  Increment when
#                       new functionality is added or new interfaces
#                       are defined, but all changes are backward
#                       compatible.
# ORCA_VER_PATCH        Orca's patch version number.  Increment for
#                       every released patch.
# ORCA_VER_QUOTED       The variables $ORCA_VER_MAJOR,
#                       $ORCA_VER_MINOR and $ORCA_VER_PATCH
#                       joined with periods, i.e. "1.2.3".
# ORCA_VER_REVISION     The Subversion repository revision number of
#                       this release.  It remains 0 in the repository.
#                       When rolling a tarball, it is automatically
#                       replaced with a best guess to be the correct
#                       revision number.
# ORCA_VER_TAG          A string describing the version.  This tag
#                       remains " (dev $ORCA_VER_REVISION)" in the
#                       repository so that we can always see that the
#                       software has been built from the repository
#                       rather than a "blessed" version.  For snapshot
#                       releases, the variable is left unchanged.  For
#                       final releases, it is emptied.
# ORCA_VERSION          The real version of Orca.  Formed by the string
#                       "$ORCA_VER_QUOTED$ORCA_VER_TAG".
# ORCA_RRD_VERSION      This is the version number used in creating the DS
#                       names in RRDs.  This should be updated any time a
#                       new version of Orca needs some new content in its
#                       RRD files.  The DS name is a concatentation of the
#                       string Orca with this string of digits.
# DAY_SECONDS           The number of seconds in one day.
# IS_WIN32              If Orca is running on a Windows platform.
use vars         qw($ORCA_VER_MAJOR
                    $ORCA_VER_MINOR
                    $ORCA_VER_PATCH
                    $ORCA_VER_QUOTED
                    $ORCA_VER_REVISION
                    $ORCA_VER_TAG
                    $ORCA_VERSION
                    $ORCA_RRD_VERSION);
push(@EXPORT_OK, qw($ORCA_VER_MAJOR
                    $ORCA_VER_MINOR
                    $ORCA_VER_PATCH
                    $ORCA_VER_QUOTED
                    $ORCA_VER_REVISION
                    $ORCA_VER_TAG
                    $ORCA_VERSION
                    $ORCA_RRD_VERSION
                    DAY_SECONDS
                    IS_WIN32));
$ORCA_VER_MAJOR    =  0;
$ORCA_VER_MINOR    = 28;
$ORCA_VER_PATCH    =  0;
$ORCA_VER_REVISION =  535;
$ORCA_VER_QUOTED   =  "$ORCA_VER_MAJOR.$ORCA_VER_MINOR.$ORCA_VER_PATCH";
$ORCA_VER_TAG      =  " (dev $ORCA_VER_REVISION)";
$ORCA_VERSION      =  "$ORCA_VER_QUOTED$ORCA_VER_TAG";
$ORCA_RRD_VERSION  =   19990222;
sub DAY_SECONDS    () { 24*60*60 };
sub IS_WIN32       () { $^O eq 'MSWin32' };

# These define the name of the different round robin archives (RRAs)
# to create in each RRD file, how many primary data points go into a
# consolidated data point, and how far back in time they go.
#
# The first RRA is every 5 minutes for 200 hours, the second is every
# 30 minutes for 31 days, the third is every 2 hours for 100 days, and
# the last is every day for 3 years.
#
# The first array holds the names of the different RRAs and is also
# used in the list of plots to create.  The second array holds the
# number of 300 second intervals are used to create a consolidated
# data point.  The third array is the number of consolidated data
# points held in the RRA.
use vars         qw(@RRA_PLOT_TYPES @RRA_PDP_COUNTS @RRA_ROW_COUNTS);
push(@EXPORT_OK, qw(@RRA_PLOT_TYPES @RRA_PDP_COUNTS @RRA_ROW_COUNTS));
BEGIN {
  @RRA_PLOT_TYPES = qw(daily weekly monthly yearly);
  @RRA_PDP_COUNTS =   (    1,     6,     24,   288);
  @RRA_ROW_COUNTS =   ( 2400,  1488,   1200,  1098);
}

# Define all of the different possible plots to create.  This
# structure allows the user via the configuration file to turn off
# particular plots to create, such the monthly one.  In addition to
# the plot types that are structured in the RRD via its RRA's, there
# is an additional hourly plot that is listed before the daily plot
# and an additional quarterly plot (100 days) created between the
# monthly and yearly plots.  The quarterly plot is updated daily.
#
# For each plot type, the first value in the array reference is the
# number of 300 second intervals are used in a plot.  The second value
# is the number of seconds graphed in the plots.  Be careful to not
# increase the time interval so much that the number of data points to
# plot are greater than the number of pixels available for the image,
# otherwise there will be a 30% slowdown due to a reduction
# calculation to resample the data to the lower resolution for the
# plot.  For example, with 40 days of 2 hour data, there are 480 data
# points.  For no slowdown to occur, the image should be at least 481
# pixels wide.
#
# The @CONST_IMAGE_PLOT_TYPES variable contains the order in which
# plots are created and all of the elements of
# @CONST_IMAGE_PLOT_TITLES should appear as keys in
# @CONST_IMAGE_PLOT_INFO.
use vars         qw(@CONST_IMAGE_PLOT_TYPES %CONST_IMAGE_PLOT_INFO);
push(@EXPORT_OK, qw(@CONST_IMAGE_PLOT_TYPES %CONST_IMAGE_PLOT_INFO));
BEGIN {
  @CONST_IMAGE_PLOT_TYPES = qw(hourly daily weekly monthly quarterly yearly);
  %CONST_IMAGE_PLOT_INFO   =
  ('hourly'    => [$RRA_PDP_COUNTS[0],   3*60*60],          #  36 data points
   'daily'     => [$RRA_PDP_COUNTS[0],   1.5*DAY_SECONDS],  # 432 data points
   'weekly'    => [$RRA_PDP_COUNTS[1],  10  *DAY_SECONDS],  # 480 data points
   'monthly'   => [$RRA_PDP_COUNTS[2],  40  *DAY_SECONDS],  # 480 data points
   'quarterly' => [$RRA_PDP_COUNTS[3], 100  *DAY_SECONDS],  # 100 data points
   'yearly'    => [$RRA_PDP_COUNTS[3], 428  *DAY_SECONDS]); # 428 data points

  # Ensure that the number of elements of @CONST_IMAGE_PLOT_TYPES
  # exactly matches the keys of %CONST_IMAGE_PLOT_INFO.
  unless (@CONST_IMAGE_PLOT_TYPES == keys %CONST_IMAGE_PLOT_INFO) {
      die "$0: internal error: number of elements in ",
          "\@CONST_IMAGE_PLOT_TYPES does not match number of keys in ",
          "\%CONST_IMAGE_PLOT_INFO.\n";
  }

  foreach my $title (@CONST_IMAGE_PLOT_TYPES) {
    unless (defined $CONST_IMAGE_PLOT_INFO{$title}) {
      die "$0: internal error: element '$title' in ",
          "\@CONST_IMAGE_PLOT_TYPES is not a key in ",
          "\%CONST_IMAGE_PLOT_INFO.\n";
    }
  }
}

# These variables hold copies of @CONST_IMAGE_PLOT_TYPES and
# @CONST_IMAGE_PLOT_INFO with only those plot types that are specified
# in the configuration file.
use vars         qw(@IMAGE_PLOT_TYPES @IMAGE_PDP_COUNTS @IMAGE_TIME_SPAN);
push(@EXPORT_OK, qw(@IMAGE_PLOT_TYPES @IMAGE_PDP_COUNTS @IMAGE_TIME_SPAN));

# This holds the length of the longest plot type string that is
# specified in the configuration file.
use vars         qw($MAX_PLOT_TYPE_LENGTH);
push(@EXPORT_OK, qw($MAX_PLOT_TYPE_LENGTH));

# These variables are set once at program start depending upon the
# command line arguments:
# $opt_daemon                   Daemonize Orca.
# $opt_generate_gifs            Generate GIFs instead of PNGs.
# $opt_log_filename             Output log filename.
# $opt_once_only                Do only one pass through Orca.
# $opt_no_html                  Do not generate any HTML files.
# $opt_no_images                Do not generate any image files.
# $opt_verbose                  Be verbose about my running.
use vars         qw($opt_daemon
                    $opt_generate_gifs
                    $opt_log_filename
                    $opt_no_html
                    $opt_no_images
                    $opt_once_only
                    $opt_verbose
                    $IMAGE_SUFFIX);
push(@EXPORT_OK, qw($opt_daemon
                    $opt_generate_gifs
                    $opt_log_filename
                    $opt_no_html
                    $opt_no_images
                    $opt_once_only
                    $opt_verbose
                    $IMAGE_SUFFIX));
$opt_daemon          = 0;
$opt_generate_gifs   = 0;
$opt_log_filename    = '';
$opt_no_html         = 0;
$opt_no_images       = 0;
$opt_once_only       = 0;
$opt_verbose         = 0;
$IMAGE_SUFFIX        = 'png';

# This constant stores the commonly used string to indicate that a
# subroutine has been passed an incorrect number of arguments.
use vars qw($INCORRECT_NUMBER_OF_ARGS);
push(@EXPORT_OK, qw($INCORRECT_NUMBER_OF_ARGS));
$INCORRECT_NUMBER_OF_ARGS = "passed incorrect number of arguments.\n";

# This subroutine is compiled once to prevent compiling of the
# subroutine sub { die $_[0] } every time an eval block is entered.
sub die_when_called {
  die $_[0];
}
push(@EXPORT_OK, qw(die_when_called));

# This contains the regular expression string to check if a string
# contains the "sub {" and "}" portions or this should be added.
use vars         qw($is_sub_re);
push(@EXPORT_OK, qw($is_sub_re));
$is_sub_re = '^\s*sub\s*{.*}\s*$';

1;
