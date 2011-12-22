# Orca::OpenFileHash: Cache open file descriptors for the whole program.
#
# $HeadURL: file:///var/www/svn/repositories-public/orcaware-public/orca/trunk/lib/Orca/OpenFileHash.pm $
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

package Orca::OpenFileHash;

use strict;
use Carp;
use Exporter;
use Orca::Constants     qw($opt_verbose);
use Orca::SourceFileIDs qw(@sfile_fids);
use vars                qw(@EXPORT_OK @ISA $VERSION);

@ISA     = qw(Exporter);
$VERSION = (substr q$Revision: 513 $, 10)/100.0;

# Set up a cache of 100 open file descriptors for the source data
# files.  This leaves a large number of free file descriptors for
# other use in the program.
use vars qw($open_file_cache);
unless ($open_file_cache) {
  $open_file_cache = Orca::OpenFileHash->new(100)
}

# Export a global open file cache object.
@EXPORT_OK = qw($open_file_cache);

# Use a blessed reference to an array as the storage for this class.
# Define these constant subroutines as indexes into the array.  If
# the order of these indexes change, make sure to rearrange the
# constructor in new.
sub I_MAX_ELEMENTS    () { 0 }
sub I_HASH            () { 1 }
sub I_WEIGHTS         () { 2 }
sub I_FILENOS         () { 3 }

# These constants are used in the array reference for a particular FID.
sub I_FID_FD      () { 0 }
sub I_FID_WEIGHT  () { 1 }
sub I_FID_IS_PIPE () { 2 }

sub new {
  unless (@_ == 2) {
    confess "$0: Orca::OpenFileHash::new passed wrong number of arguments.\n";
  }

  my ($class, $max_elements) = @_;

  bless [$max_elements, {}, {}, {}], $class;
}

sub open {
  unless (@_ == 3) {
    confess "$0: Orca::OpenFileHash::open passed wrong number of arguments.\n";
  }

  my ($self, $fid, $weight) = @_;

  local *FD;

  # Uncompress compressed files on the fly and read them in.
  my $filename = $sfile_fids[$fid];
  my $is_pipe = 1;
  if ($filename =~ /\.gz$/) {
    $filename = "gunzip -c $filename |";
  } elsif ($filename =~ /\.Z$/) {
    $filename = "uncompress -c $filename |";
  } elsif ($filename =~ /\.bz2$/) {
    $filename = "bunzip2 -c $filename |";
  } else {
    $is_pipe = 0;
  }

  # Try to open the file or pipe.  If the open fails and if there are
  # other opened files, then reduce the maximum number of open files.
  # If this is the first open file and the pipe fails, then do not
  # attempt to open it again.
  my $open_error = 0;
  while (!open(FD, $filename)) {
    my $num_current_open_files = keys %{$self->[I_HASH]};
    warn "$0: warning: cannot open '$filename' for reading: $!\n";
    warn "$0: warning: there are current $num_current_open_files open source ",
         "files.\n";
    return unless $num_current_open_files;

    $num_current_open_files -= 2;
    return if $num_current_open_files <= 4;
    warn "$0: warning: shrinking maximum number open files to ",
         "$num_current_open_files.\n";

    $self->[I_MAX_ELEMENTS] = $num_current_open_files;
    $self->_close_extra($num_current_open_files-1);
    $open_error = 1;
  }

  if ($open_error) {
    warn "$0: warning: finally able to open '$filename' for reading.\n";
  }

  $self->add($fid, $weight, *FD, $is_pipe);

  *FD;
}

sub add {
  unless (@_ == 5) {
    confess "$0: Orca::OpenFileHash::add passed wrong number of arguments.\n";
  }

  my ($self, $fid, $weight, $fd, $is_pipe) = @_;

  # If there is an open file descriptor for this fid, then force it
  # to close.  Then make space for the new file descriptor in the
  # cache.
  $self->close($fid);
  $self->_close_extra($self->[I_MAX_ELEMENTS] - 1);

  my $fileno = fileno($fd);

  $self->[I_HASH]{$fid}[I_FID_FD]      = $fd;
  $self->[I_HASH]{$fid}[I_FID_WEIGHT]  = $weight;
  $self->[I_HASH]{$fid}[I_FID_IS_PIPE] = $is_pipe;
  $self->[I_FILENOS]{$fid}             = $fileno;

  unless (defined $self->[I_WEIGHTS]{$weight}) {
    $self->[I_WEIGHTS]{$weight} = [];
  }
  push(@{$self->[I_WEIGHTS]{$weight}}, $fid);
}

sub close {
  my ($self, $fid) = @_;

  my $data_ref = delete $self->[I_HASH]{$fid};
  return $self unless $data_ref;

  my $filename    = $sfile_fids[$fid];
  my $fd          = $data_ref->[I_FID_FD];
  my $weight      = $data_ref->[I_FID_WEIGHT];
  my $is_pipe     = $data_ref->[I_FID_IS_PIPE];
  my $is_eof      = $is_pipe ? eof($fd) : 0;
  my $close_value = close($fd);
  unless ($close_value) {
    if ($is_pipe) {
      if ($is_eof) {
        warn "$0: warning: cannot close pipe for '$filename': ",
             "[$close_value \$?=$?] $!\n" if $opt_verbose > 1;
      }
    } else {
      warn "$0: warning: cannot close '$filename': [$close_value] $!\n";
    }
  }

  my $fileno = delete $self->[I_FILENOS]{$fid};

  my @fids = grep { $_ != $fid } @{$self->[I_WEIGHTS]{$weight}};
  if (@fids) {
    $self->[I_WEIGHTS]{$weight} = \@fids;
  } else {
    delete $self->[I_WEIGHTS]{$weight};
  }

  $close_value;
}

sub _close_extra {
  my ($self, $max_elements) = @_;

  # Remove this number of elements from the structure.
  my $close_number = (keys %{$self->[I_HASH]}) - $max_elements;

  return $self unless $close_number > 0;

  my @weights = sort { $a <=> $b } keys %{$self->[I_WEIGHTS]};

  while ($close_number > 0) {
    my $weight = shift(@weights);
    foreach my $fid (@{$self->[I_WEIGHTS]{$weight}}) {
      $self->close($fid);
      --$close_number;
    }
  }

  $self;
}

sub change_weight {
  my ($self, $fid, $new_weight) = @_;

  return unless defined $self->[I_HASH]{$fid};

  my $old_weight = $self->[I_HASH]{$fid}[I_FID_WEIGHT];
  return if $old_weight == $new_weight;

  # Save the new weight.
  $self->[I_HASH]{$fid}[I_FID_WEIGHT] = $new_weight;

  unless (defined $self->[I_WEIGHTS]{$new_weight}) {
    $self->[I_WEIGHTS]{$new_weight} = [];
  }
  push(@{$self->[I_WEIGHTS]{$new_weight}}, $fid);

  # Remove the old weight.
  my @fids = @{$self->[I_WEIGHTS]{$old_weight}};
  @fids = grep { $_ != $fid } @fids;
  if (@fids) {
    $self->[I_WEIGHTS]{$old_weight} = \@fids;
  } else {
    delete $self->[I_WEIGHTS]{$old_weight};
  }

  1;
}

sub get_fd {
  my ($self, $fid) = @_;

  if (defined (my $ref = $self->[I_HASH]{$fid})) {
    return $ref->[I_FID_FD];
  } else {
    return;
  }
}

sub is_pipe {
  my ($self, $fid) = @_;

  if (defined (my $ref = $self->[I_HASH]{$fid})) {
    return $ref->[I_FID_IS_PIPE];
  } else {
    return;
  }
}

sub is_open {
  defined $_[0]->[I_HASH]{$_[1]};
}

1;
