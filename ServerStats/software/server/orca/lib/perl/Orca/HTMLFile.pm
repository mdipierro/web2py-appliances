# Orca::HTMLFile: Manage the creation of HTML files.
#
# $HeadURL: file:///var/www/svn/repositories-public/orcaware-public/orca/trunk/lib/Orca/HTMLFile.pm $
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

package Orca::HTMLFile;

use strict;
use Carp;
use Orca::Constants qw($ORCA_VERSION);
use vars            qw(@EXPORT_OK @ISA $VERSION);
@ISA     = qw(Exporter);
$VERSION = (substr q$Revision: 513 $, 10)/100.0;

# $html_hr is the HTML <hr/> tag with the correct width attribute.
use vars         qw($html_hr);
push(@EXPORT_OK, qw($html_hr));
$html_hr = '<hr align="left" width="692" />';

# Use a blessed reference to an array as the storage for this class.
# Define these constant subroutines as indexes into the array.  If
# the order of these indexes change, make sure to rearrange the
# constructor in new.
sub I_FILENAME () { 0 }
sub I_FD       () { 1 }
sub I_BOTTOM   () { 2 }

sub new {
  unless (@_ == 4 or @_ == 5) {
    confess "$0: Orca::HTMLFile::new passed wrong number of arguments.\n";
  }
  my ($class, $filename, $title, $top, $bottom) = @_;
  $bottom = '' unless defined $bottom;

  local *FD;
  unless (open(FD, "> $filename.htm")) {
    $@ = "cannot open '$filename.htm' for writing: $!";
    return;
  }

  print FD <<END;
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
  <head>
    <title>Orca - $title</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="robots" content="index, follow">
  </head>

  <body bgcolor="#ffffff">

    <!-- Created by Orca version $ORCA_VERSION -->
    <!-- Created using RRDtool version $RRDs::VERSION -->
    <!-- Created using Perl $] -->

    $top

    <h1>$title</h1>
END

  bless [$filename, *FD, $bottom], $class;
}

sub print {
  my $self = shift;
  print { $self->[I_FD] } "@_";
}

my $i_bottom = I_BOTTOM;

sub DESTROY {
  my $self = shift;

  if ($self->[$i_bottom] =~ /\S/) {
    print { $self->[I_FD] } $self->[$i_bottom], "\n<br />\n", $html_hr, "\n";
  }

  print { $self->[I_FD] } <<END;

    <table cellpadding="0" border="0">
      <tr valign="bottom">
        <td width="186">
          <a href="http://www.orcaware.com/orca/">
            <img width="186" height="45" border="0"
                 src="orca_logo.gif" alt="Orca home page"></a>
        </td>
        <td width="20">&nbsp;&nbsp</td>

        <td width="334">
          <a href="http://www.rothschildimage.com/">
            <img width="334" height="21" border="0"
                 src="rothschild_image_logo.png"
                 alt="The Rothschild Image home page" /></a>
        </td>
        <td width="20">&nbsp;&nbsp;</td>
        <td width="120">
          <a href="http://people.ee.ethz.ch/~oetiker/webtools/rrdtool/">
            <img width="120" height="34" border="0" src="rrdtool_logo.gif"
                 alt="RRDtool home page"></a>
        </td>
      </tr>

      <tr valign="top">
        <td width="186">
          <font face="verdana,geneva,arial,helvetica" size="2">
            <a href="http://www.orcaware.com/orca/">Orca</a> $ORCA_VERSION
            by<br />
            <a href="http://www.orcaware.com/">Blair Zajac</a><br />
            <!-- See http://www.cdt.org/speech/spam/030319spamreport.shtml for
                 evidence that this has some effect. -->
            <a href="mailto:&#098;&#108;&#097;&#105;&#114;&#064;&#111;&#114;&#099;&#097;&#119;&#097;&#114;&#101;&#046;&#099;&#111;&#109;">
              &#098;&#108;&#097;&#105;&#114;&#064;&#111;&#114;&#099;&#097;&#119;&#097;&#114;&#101;&#046;&#099;&#111;&#109;</a>
          </font>
        </td>
        <td width="20">&nbsp;&nbsp;</td>

        <td width="334">
          <font face="verdana,geneva,arial,helvetica" size="2">
             Funding for Orca provided by renowned fashion
             <a href="http://www.rothschildimage.com/">image consultant</a>
             and <a href="http://www.rothschildimage.com/seminars.html">extreme
             makeover</a> guru, Ashley Rothschild.
           </font>
        </td>
        <td width="20">&nbsp;&nbsp;</td>
        <td width="120">
          <font face="verdana,geneva,arial,helvetica" size="2">
            Graphs made available by RRDtool.
          </font>
        </td>
      </tr>
    </table>
  </body>
</html>
END

  my $filename = $self->[I_FILENAME];
  close($self->[I_FD]) or
    warn "$0: warning: cannot close '$filename.htm': $!\n";
  rename("$filename.htm", $filename) or
    warn "$0: cannot rename '$filename.htm' to '$filename': $!\n";
}

1;
