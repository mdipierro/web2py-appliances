# Orca::SourceFileIDs: Associate long filenames with numeric
# identifiers.  The primary purpose of this module is to keep only two
# copies of all the filenames used by Orca.
#
# $HeadURL: file:///var/www/svn/repositories-public/orcaware-public/orca/trunk/lib/Orca/SourceFileIDs.pm $
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

package Orca::SourceFileIDs;

use strict;
use Carp;
use Math::IntervalSearch qw(interval_search);
use vars                 qw(@EXPORT_OK @ISA $VERSION);

@ISA     = qw(Exporter);
$VERSION = (substr q$Revision: 513 $, 10)/100.0;

# This module contains three variables.  The first is a hash keyed by
# filename with a numeric value.  The second is an array, where value
# associated with a particular index is the filename.  The third is a
# list of unused FIDs that have FID smaller than the maximum FID.
# This list should really only be used by the Orca::State package.
# This structure should not grow too large, as files are removed and
# their space will be allocated by the next new file.
use vars     qw(%sfile_fids @sfile_fids @sfile_unused_fids);
@EXPORT_OK = qw(%sfile_fids @sfile_fids @sfile_unused_fids);

# The users of these variables are allowed to either add or remove a
# file from the list of FIDs and to clear the list of FIDs.
push(@EXPORT_OK, qw(new_fids delete_fid clear_fids));

# Users of these modules will need to register either names of arrays
# or references to arrays that are indexed by FIDs so that when array
# truncation is done, these arrays may also be truncated.
push(@EXPORT_OK, qw(register_fid_arrays));

# Register references to arrays indexed by FIDs.  Make sure that each
# array is only registered once.
my %registered_arrays;
my @registered_arrays;
sub register_fid_arrays {
  my $caller_package = caller;
  foreach my $ref (@_) {
    # Check the validity of the reference.  It needs to be either a
    # variable name or a reference to an array.
    if (ref $ref) {
      # The reference should be a reference to an array.
      unless (UNIVERSAL::isa($ref, "ARRAY")) {
        confess "$0: internal error: Orca::SourceFileIDs::register_fid_arrays passed non-array reference.\n";
      }
    } else {
      my ($type, $symbol) = unpack('a1a*', $ref);
      unless ($type eq '@') {
        confess "$0: internal error: Orca::SourceFileIDs::register_fid_arrays passed non-array variable name '$ref'.\n";
      }
      if ($symbol =~ /::/) {
        confess "$0: internal error: Orca::SourceFileIDs::register_fid_arrays cannot pass somebody else's variables.\n";
      }
      no strict 'refs';
      $ref = \@{"${caller_package}::$symbol"};
      use strict;
    }
    next if defined $registered_arrays{$ref};
    $registered_arrays{$ref} = 1;
    push(@registered_arrays, $ref);
  }
}

sub new_fids {
  my @fids;
  foreach my $filename (@_) {
    # Use the FID if the filename is already defined.
    my $fid = $sfile_fids{$filename};
    if (defined $fid) {
      push(@fids, $fid);
      next;
    }

    # If there are any deleted FIDs, then take that space, otherwise
    # put a FID at the end of the list.
    if (@sfile_unused_fids) {
      $fid = shift(@sfile_unused_fids);
    } else {
      $fid = $#sfile_fids + 1;
    }

    $sfile_fids[$fid] = $filename;
    foreach my $ref (@registered_arrays) {
      $ref->[$fid] = 'NEW';
    }

    $sfile_fids{$filename} = $fid;
    push(@fids, $fid);
  }
  @fids;
}

# Remove a given filename from the list of FIDs.
sub delete_fid {
  my $filename = shift;

  my $fid = delete $sfile_fids{$filename};
  return unless defined $fid;

  # Now manage the deleted FID.  There are several different cases to
  # handle.  If the FID was the highest numbered FID in the array,
  # then we need to shorten sfile_fids and any registerd arrays and
  # also check if any smaller deleted FIDs are next to the deleted
  # FID.  The case to handle here is if all the FIDs other than the
  # largest FID are deleted and then the largest FID is deleted, then
  # all of the already deleted FIDs need to be forgotten.  If the FID
  # was not the largest FID, then just add it to the list of unused
  # FIDs.
  if ($fid = $#sfile_fids) {
    my $remove_count = 1;
    --$#sfile_fids;
    while (@sfile_unused_fids and $sfile_unused_fids[-1] = $#sfile_fids) {
      --$#sfile_unused_fids;
      --$#sfile_fids;
      ++$remove_count;
    }
    foreach my $ref (@registered_arrays) {
      $#$ref -= $remove_count;
    }
  } else {
    $sfile_fids[$fid] = undef;
    foreach my $ref (@registered_arrays) {
      $ref->[$fid] = undef;
    }
    my $index = interval_search($fid, \@sfile_unused_fids) + 1;
    splice(@sfile_unused_fids, $index, 0, $fid);
  }
}

sub clear_fids {
  undef %sfile_fids;
  undef @sfile_fids;
  undef @sfile_unused_fids;
  foreach my $ref (@registered_arrays) {
    undef @$ref;
  }
}

# Remove any empty FIDs from the list of FIDs.  Return the number of
# FIDs removed.
sub _not_working_compress_fids {
  return 0 unless @sfile_unused_fids;

  my $count = @sfile_unused_fids;

  # Go through all the FIDs in descending numeric order.  If the
  # undefined fid is at the end of the array, then just shrink the
  # array.  Otherwise take the last FID and place it in the space of
  # the undefined FID.
  foreach my $fid (sort {$b <=> $a} @sfile_unused_fids) {
    # If the FID is not the last one, then copy the last FID into the space.
    if ($fid != $#sfile_fids) {
      $sfile_fids[$fid] = $sfile_fids[-1];
    }

    # Shrink the array.
    --$#sfile_fids;
  }

  @sfile_unused_fids = ();

  $count;
}

1;
