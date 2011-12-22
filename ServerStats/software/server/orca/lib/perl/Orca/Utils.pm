# Orca::Utils: Small utility subroutines.
#
# $HeadURL: file:///var/www/svn/repositories-public/orcaware-public/orca/trunk/lib/Orca/Utils.pm $
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

package Orca::Utils;

use strict;
use Carp;
use Exporter;
use Digest::MD5         qw(md5_base64);
use Orca::Constants     qw($INCORRECT_NUMBER_OF_ARGS);
use Orca::Config        qw(%config_global);
use Orca::SourceFileIDs qw(new_fids);
use vars qw(@EXPORT_OK @ISA $VERSION);

@EXPORT_OK = qw(capatialize
                email_message
                gcd
                name_to_fsname
                perl_glob
                print_running_stats
                recursive_mkdir
                unique);
@ISA       = qw(Exporter);
$VERSION   = (substr q$Revision: 513 $, 10)/100.0;

# Take a string and capatialize only the first character of the
# string.
sub capatialize {
  my $string = shift;
  substr($string, 0, 1) = uc(substr($string, 0, 1));
  $string;
}

# Email the list of people a message.
sub email_message {
  my ($people, $subject) = @_;

  return unless $people;

  if (open(SENDMAIL, "|/usr/lib/sendmail -oi -t")) {
    print SENDMAIL <<"EOF";
To: $people
Subject: Orca: $subject

Orca: $subject
EOF
    close(SENDMAIL) or
      warn "$0: warning: sendmail did not close: $!\n";
  } else {
    warn "$0: warning: cannot fork for sendmail: $!\n";
  }
}

# Return the greatest common divisor.
sub gcd {
  unless (@_ == 2) {
    confess "$0: Orca::Utils::gcd $INCORRECT_NUMBER_OF_ARGS";
  }
  my ($m, $n) = @_;
  if ($n > $m) {
    my $tmp = $n;
    $n = $m;
    $m = $tmp;
  }
  while (my $r = $m % $n) {
    $m = $n;
    $n = $r;
  }
  $n;
}

# Replace special characters from names, remove redundant characters,
# and shorten the names so the maximum path name is not exceeded.  If
# the name is still too long such that the maximum filename path
# length ($config_global{max_filename_length}) may be exceeded by
# appending -daily.html or other names to the name, then compute a MD5
# hash of the name, trim the name the name to max_filename_length
# minus at least 23 plus the postfix length characters to leave space
# for a 22 byte base64 MD5 digest, plus a separating '-', and plus the
# postfix.
sub name_to_fsname {
  unless (@_ == 2) {
    confess "$0: Orca::Utils::name_to_fsname $INCORRECT_NUMBER_OF_ARGS";
  }

  my ($name, $postfix_length) = @_;

  $name =~ s/:/_/g;

  # When Internet Explorer sees a \ in a URL, it converts it into a /
  # when it makes a request to a web server which will fail, so change
  # the \ to a |.
  $name =~ s:\\:|:g;

  # A / cannot appear in a filename because it'll look like a
  # directory.
  $name =~ s:/:_per_:g;

  $name =~ s:\s+:_:g;
  $name =~ s:%:_pct_:g;
  $name =~ s:#:_num_:g;
  $name =~ s:\?:_Q_:g;
  $name =~ s:\*:_X_:g;

  # Trim anything containing orcallator and orca to o.
  $name =~ s:orcallator:o:g;
  $name =~ s:orca:o:g;

  # Remove trailing _'s.
  $name =~ s:_+$::;
  $name =~ s:_+,:,:g;

  # Replace multiple _'s with one _, except when they follow a , which
  # happens when the same group and subgroup appear for a new data
  # source.
  $name =~ s:,_{2,}:\200:g;
  $name =~ s:_{2,}:_:g;
  $name =~ s:\200:,__:g;

  my $max_filename_length = $config_global{max_filename_length};
  if (length($name)+$postfix_length > $max_filename_length) {

    my $md5         = md5_base64($name);
    my $trim_length = $max_filename_length - 23 - $postfix_length;
    $name           = substr($name, 0, $trim_length) . "-$md5";

    # Be careful to convert any / or + characters to _ and any \'s to
    # |'s.  The / character needs to be changed since / is a valid
    # base64 character and can't be used since we don't want a
    # directory.
    $name =~ s:[/\+]:_:g;
    $name =~ s:[\\]:|:g;
  }

  $name;
}

# Find all files matching a particular Perl regular expression and
# return file ids.
sub perl_glob {
  my $regexp = shift;

  # perl_glob gets called recursively.  To tell if we're being called by
  # perl_glob, look for the existence of two arguments, where the second
  # one if the current directory to open for matching.
  my $current_dir = @_ ? $_[0] : '.';

  # Remove all multiple /'s, since they will confuse perl_glob.
  $regexp =~ s:/{2,}:/:g;

  # If the regular expression begins with a /, then remove it from the
  # regular expression and set the current directory to /.
  $current_dir = '/' if $regexp =~ s:^/::;

  # Get the first file path element from the regular expression to
  # match.
  my @regexp_elements = split(m:/:, $regexp);
  my $first_regexp    = shift(@regexp_elements);

  # Find all of the files in the current directory that match the
  # first regular expression.
  unless (opendir(GLOB_DIR, "$current_dir")) {
    warn "$0: error: cannot opendir '$current_dir': $!\n";
    return ();
  }

  my @matches = grep { /^$first_regexp$/ } readdir(GLOB_DIR);

  closedir(GLOB_DIR) or
    warn "$0: warning: cannot closedir '$current_dir': $!\n";

  # If the last path element is being used as the regular expression,
  # then just return the list of matching files with the current
  # directory prepended.
  unless (@regexp_elements) {
    @matches = grep { -f $_ and -r _ } map { "$current_dir/$_" } @matches;
    return @_ ? @matches : new_fids(@matches);
  }

  # Otherwise we need to look into the directories below the current
  # directory.  Also create the next regular expression to use that is
  # made up of the remaining file path elements.  Make sure not to
  # process any directories named '..'.
  my @results;
  my $new_regexp = join('/', @regexp_elements);
  foreach my $new_dir (grep { $_ ne '..' and -d "$current_dir/$_" } @matches) {
    my $new_current = "$current_dir/$new_dir";
    $new_current =~ s:/{2,}:/:g;
    push(@results, perl_glob($new_regexp, $new_current));
  }

  return @_ ? @results : new_fids(@results);
}

# Print a message on the statistics of this running process.  Note the
# starting time of the script.
my $start_time = time;
sub print_running_stats {
  my $time_span = time - $start_time;
  my $minutes   = int($time_span/60);
  my $seconds   = $time_span - 60*$minutes;

  printf "Current running time is %d:%02d minutes.\n", $minutes, $seconds;
}

# Given a directory name, attempt to make all necessary directories.
sub recursive_mkdir {
  my $dir = shift;

  # Remove extra /'s.
  $dir =~ s:/{2,}:/:g;

  my $path;
  if ($dir =~ m:^/:) {
    $path = '/';
  } else {
    $path = './';
  }

  my @elements = split(/\//, $dir);
  foreach my $element (@elements) {
    $path = "$path/$element";
    next if -d $path;
    unless (mkdir($path, 0755)) {
      die "$0: error: unable to create '$path': $!\n";
    }
  }
}

# Return a list of the unique elements of a list in the same order as
# they appear in the input list.
sub unique {
  my %a;
  my @unique;
  foreach my $element (@_) {
    unless (exists $a{$element}) {
      push(@unique, $element);
      $a{$element} = 1;
    }
  }
  @unique;
}

1;
