# Orca::NewState: Keep state information between invocations of Orca.
#
# $HeadURL: file:///var/www/svn/repositories-public/orcaware-public/orca/trunk/lib/Orca/NewState.pm $
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

package Orca::NewState;

use strict;
use Carp;
use Storable        qw(nstore_fd retrieve_fd);
use Orca::Constants qw($opt_verbose
                       die_when_called);
use vars            qw(@EXPORT_OK @ISA $VERSION);

@ISA     = qw(Exporter);
$VERSION = (substr q$Revision: 513 $, 10)/100.0;

# Create one global state object for the whole program.
use vars      qw($orca_state);
@EXPORT_OK  = qw($orca_state);
$orca_state = Orca::NewState->new;

# This defines the minimum version of saved state file required.
my $required_version = "1.0";

# The following variables are stored from and restored to from the
# given packages.  While importing the packages are not necessary,
# they do provide error checking in case a mistake is made in
# naming a package name and/or variable.
use vars qw(@source_file_ids @source_files);
BEGIN {
  @source_file_ids = qw(%sfile_fids
                        @sfile_fids
                        @sfile_unused_fids);
  @source_files    = qw(@sfile_file_dev
                        @sfile_file_ino
                        @sfile_file_mtime
                        @sfile_last_stat_time
                        @sfile_last_read_time
                        @sfile_last_data_time
                        @sfile_cid);
}
use Orca::SourceFileIDs @source_file_ids;
use Orca::SourceFiles   @source_files;

# This is a list of references to objects to save and restore.
my @store_restore_list;

# This subroutine takes a package name and a list of variable names in that
# package that should be saved.  Using the package and variable names, it
# goes into Perl's symbol table to get references to these variables.
sub save_variables {
  my ($caller_package, @vars) = @_;
  foreach my $var (@vars) {
    my ($type, $symbol) = unpack('a1a*', $var);
    no strict 'refs';
    push(@store_restore_list,
      $type eq '$' ? \$ {"${caller_package}::$symbol"} :
      $type eq '@' ? \@ {"${caller_package}::$symbol"} :
      $type eq '%' ? \% {"${caller_package}::$symbol"} :
      do {
        confess "$0: internal error: Orca::NewState::save_variables cannot save '$var'.\n";
      }
    );
    use strict;
  }
}
save_variables('Orca::SourceFileIDs', @source_file_ids);
save_variables('Orca::SourceFiles',   @source_files);

sub new {
  unless (@_ == 1 or @_ == 2) {
    confess "$0: Orca::NewState::new passed wrong number of arguments.\n";
  }

  my $class = shift;

  my $self = bless {}, $class;

  if (@_) {
    $self->load(@_);
  }

  $self;
}

sub exists {
  unless (@_ == 2) {
    confess "$0: Orca::NewState::exists passed wrong number of arguments.\n";
  }

  exists $_[0]->{$_[1]};
}

sub fetch {
  $_[0]->{$_[1]};
}

sub load {
  unless (@_ == 2) {
    confess "$0: Orca::NewState::load passed wrong number of arguments.\n";
  }

  my ($self, $filename) = @_;

  return unless -r $filename;

  print "Loading state from '$filename'.\n" if $opt_verbose;

  if (open(STATE, $filename)) {
    binmode(STATE);
    my $result = $self->_load_state($filename, \*STATE);
    close(STATE) or
      warn "$0: error in closing '$filename' for reading: $!\n";
    if (defined $result) {
      return $result;
    } else {
      warn "$0: cannot use state file '$filename'.\n";
      return;
    }
  } else {
    warn "$0: cannot open '$filename' for reading: $!.\n";
    return;
  }
}

sub _load_state {
return;
  unless (@_ == 3) {
    confess "$0: Orca::NewState::load passed wrong number of arguments.\n";
  }

  my ($self, $filename, $fd) = @_;

  # Determine the version of the state file and ignore it if it is an old
  # version.
  my $line = <$fd>;
  chomp($line);
  unless ($line) {
    warn "$0: ignoring unknown version state file '$filename'.\n";
    return;
  }
  if ($line =~ /_filename/) {
    warn "$0: ignoring old state file '$filename'.\n";
    return;
  }
  my ($version, $number_objects) = $line =~ /(\d+\.\d+)\D+(\d+)/;
  unless ($version) {
    warn "$0: ignoring unknown version state file '$filename'.\n";
    return;
  }
  if ($version < $required_version) {
    warn "$0: ignoring old $version state file '$filename' when version $required_version is required.\n";
    return;
  }
  unless ($number_objects) {
    warn "$0: cannot detmine number of objects in state file '$filename'.\n";
    return;
  }
  unless ($number_objects == @store_restore_list) {
    warn "$0: incorrect number of saved objects in state file '$filename'.\n";
    return;
  }

  # Go through all of the objects, try to load them in, and if they all are
  # loaded, then copy them over to the final location.
  my @restored_objects;
  my $ok = 1;
  {
    eval {
      local $SIG{__DIE__}  = 'DEFAULT';
      local $SIG{__WARN__} = \&die_when_called;
      foreach (@store_restore_list) {
        my $data = retrieve_fd($fd);
        if ($data) {
          push(@restored_objects, $data);
        } else {
          $ok = 0;
          last;
        }
      }
    };
  }
  if ($@) {
    warn "$0: warning: cannot read state file '$filename': $@\n";
    return;
  } elsif (!$ok) {
    warn "$0: warning: cannot load data from state file '$filename': $!\n";
    return;
  }

  # Copy the loaded data into the final location.
  for (my $i=0; $i<@store_restore_list; ++$i) {
    my $ref = $store_restore_list[$i];
    if (UNIVERSAL::isa($ref, "SCALAR")) {
      $$ref = ${$restored_objects[$i]};
    } elsif (UNIVERSAL::isa($ref, "ARRAY")) {
      @$ref = @{$restored_objects[$i]};
    } elsif (UNIVERSAL::isa($ref, "HASH")) {
      %$ref = %{$restored_objects[$i]};
    } else {
      die "$0: internal error: restoring a ", ref($ref), " which is unknown.\n";
    }
  }
  1;
}

sub flush {
  unless (@_ == 2) {
    confess "$0: Orca::NewState::flush passed wrong number of arguments.\n";
  }

  my ($self, $filename) = @_;
  my $tmp_filename      = "$filename.tmp";
  print "Saving state into '$filename'.\n" if $opt_verbose;

  unless (open(STATE, "> $tmp_filename")) {
    warn "$0: cannot open '$tmp_filename' for writing: $!\n";
    return;
  }

  print STATE "Orca state file version $required_version with ",
    scalar(@store_restore_list), " saved objects.\n";

  # Write the saved objects to disk.
  my $result = 1;
  foreach my $ref (@store_restore_list) {
    $result = $result && nstore_fd($ref, \*STATE);
  }

  unless ($result) {
    warn "$0: error in writing to '$tmp_filename': $!\n";
  }

  unless (close(STATE)) {
    $result = 0;
    warn "$0: error in closing '$tmp_filename' for writing: $!\n";
  }

  unless ($result) {
    warn "$0: cannot flush state to file '$tmp_filename': $!\n";
    unlink($tmp_filename) or
      warn "$0: error in unlinking '$tmp_filename': $!\n";
    return;
  }

  unless (rename($tmp_filename, $filename)) {
    warn "$0: cannot rename '$tmp_filename' to '$filename': $!\n";
    return;
  }

  1;
}

1;
