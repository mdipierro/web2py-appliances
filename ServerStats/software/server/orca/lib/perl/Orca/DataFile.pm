# Orca::DataFile: Base class for managing source data, RRD and image files.
#
# $HeadURL: file:///var/www/svn/repositories-public/orcaware-public/orca/trunk/lib/Orca/DataFile.pm $
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

package Orca::DataFile;

use strict;
use Carp;
use Exporter;
use Orca::SourceFileIDs qw(@sfile_fids);
use vars                qw(@ISA @EXPORT_OK $VERSION);

@ISA       = qw(Exporter);
@EXPORT_OK = qw(ORCA_DATAFILE_LAST_INDEX);
$VERSION   = (substr q$Revision: 513 $, 10)/100.0;

# Use a blessed reference to an array as the storage for this class.
# Define these constant subroutines as indexes into the array.
sub I_FID                    () { 0 }
sub I_LAST_STAT_TIME         () { 1 }
sub I_FILE_DEV               () { 2 }
sub I_FILE_INO               () { 3 }
sub I_FILE_SIZE              () { 4 }
sub I_FILE_MTIME             () { 5 }
sub ORCA_DATAFILE_LAST_INDEX () { 5 }

sub new {
  unless (@_ == 2) {
    confess "$0: Orca::DataFile::new passed wrong number of arguments.\n";
  }

  my ($class, $fid) = @_;

  confess "$0: fid not passed to $class.\n" unless defined($fid);
  confess "$0: numeric fid not passed to $class.\n" unless $fid =~ /^\d+$/;
  my $self = bless [$fid, -1, -1, -1, -1, -1], $class;
  $self;
}

sub fid {
  $_[0]->[I_FID];
}

sub last_stat_time {
  $_[0]->[I_LAST_STAT_TIME];
}

sub file_dev {
  $_[0]->[I_FILE_DEV];
}

sub file_ino {
  $_[0]->[I_FILE_INO];
}

sub file_size {
  $_[0]->[I_FILE_SIZE];
}

sub file_mtime {
  $_[0]->[I_FILE_MTIME];
}

# Return 1 if the file exists, 0 otherwise.
sub update_stat {
  my $self = shift;

  # Only update the stat if the previous stat occured more than one
  # second ago.  This is used when this function is called immediately
  # after the object has been constructed and when we don't want to
  # call two stat's immediately.  The tradeoff is to call time()
  # instead.
  my $time = time;
  if ($time > $self->[I_LAST_STAT_TIME] + 1) {
    if (my @stat = stat($sfile_fids[$self->[I_FID]])) {
      @$self[I_FILE_DEV, I_FILE_INO, I_FILE_SIZE, I_FILE_MTIME] =
        @stat[0, 1, 7, 9];
    } else {
      @$self[I_FILE_DEV, I_FILE_INO, I_FILE_SIZE, I_FILE_MTIME] =
        (-1, -1, -1, -1);
    }
    $self->[I_LAST_STAT_TIME] = $time;
  }

  $self->[I_FILE_MTIME] != -1;
}

# Return a status depending upon the file:
#   -1 if the file does not exist.
#    0 if the file has not been updated since the last status check.
#    1 if the file has been updated since the last status check.
#    2 if the file has a new device or inode since the last status check.
sub status {
  my $self = shift;

  # Save the old state.
  my ($fid, $file_dev, $file_ino, $file_size, $file_mtime) =
    @$self[I_FID, I_FILE_DEV, I_FILE_INO, I_FILE_SIZE, I_FILE_MTIME];

  my $result = 0;
  if ($self->update_stat) {
    if ($self->[I_FILE_DEV] != $file_dev or
        $self->[I_FILE_INO] != $file_ino) {
      $result = 2;
    } elsif ($self->[I_FILE_MTIME] != $file_mtime or
           $self->[I_FILE_SIZE]  != $file_size) {
      $result = 1;
    }
  } else {
    $result = -1;
  }

  $result;
}

1;
