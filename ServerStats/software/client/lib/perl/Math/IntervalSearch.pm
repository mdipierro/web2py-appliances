package Math::IntervalSearch;

require 5.004_01;

use strict;
use vars qw(@EXPORT_OK @ISA $VERSION);
use Exporter;
use Carp;

@EXPORT_OK = qw(interval_search);
@ISA       = qw(Exporter);
$VERSION   = substr q$Revision: 1.05 $, 10;

sub cluck { warn Carp::longmess @_ }

sub LessThan {
  $_[0] < $_[1];
}

sub LessThanEqualTo {
  $_[0] <= $_[1];
}

# This holds the result from the last interval search.
my $last_interval_result = undef;

sub interval_search {
  if ( @_ > 4 ) {
    cluck "interval called with too many parameters";
    return;
  }

  # Get the input arguments.
  my $x           = shift;
  my $sequenceRef = shift;

  return unless defined($x);
  return unless defined($sequenceRef);
  return unless ref($sequenceRef);

  # Check the input arguments for any code references and use them.
  my $LessThan        = \&LessThan;
  my $LessThanEqualTo = \&LessThanEqualTo;
  @_ and defined(ref($_[0])) and ref($_[0]) eq 'CODE' and
    $LessThan = shift;
  @_ and defined(ref($_[0])) and ref($_[0]) eq 'CODE' and
    $LessThanEqualTo = shift;

  # Get the number of points in the data.
  my $num = @$sequenceRef;

  # Return -1 if there's no data.
  if ( $num <= 0 ) {
    $last_interval_result = 0;
    return -1;
  }

  # Use the result from the last time through the subroutine, if it
  # exists.  Force the result into the range required by the array
  # size.
  $last_interval_result = 0 unless defined($last_interval_result);

  # Which side of the data point is x on if there's only one point?
  if ( $num == 1 ) {
    $last_interval_result = 0;
    if ( &$LessThan($x, $sequenceRef->[0]) ) {
      return -1;
    }
    else {
      return 0;
    }
  }

  # Is the point less than the smallest point in the sequence?
  if ( &$LessThan($x, $sequenceRef->[0]) ) {
    $last_interval_result = 0;
    return -1;
  }

  # Is the point greater than the largest point in the sequence?
  if ( &$LessThanEqualTo($sequenceRef->[$num-1], $x) ) {
    return $last_interval_result = $num - 1;
  }

  # Use the result from the last run as a start for this run.
  if ( $last_interval_result > $num-1 ) {
    $last_interval_result = $num - 2;
  }
  my $ilo = $last_interval_result;
  my $ihi = $ilo + 1;

  # Is the new upper ihi beyond the extent of the sequence?
  if ( $ihi >= $num ) {
    $ihi = $num - 1;
    $ilo = $ihi - 1;
  }

  # If x < sequence(ilo), then decrease ilo to capture x.
  if ( &$LessThan($x, $sequenceRef->[$ilo]) ) {
    my $istep = 1;
    for (;;) {
      $ihi = $ilo;
      $ilo = $ihi - $istep;
      if ( $ilo <= 0 ) {
	$ilo = 0;
	last;
      }
      if ( &$LessThanEqualTo($sequenceRef->[$ilo], $x) ) {
	last;
      }
      $istep *= 2;
    }
  }

  # If x >= sequence(ihi), then increase ihi to capture x.
  if ( &$LessThanEqualTo($sequenceRef->[$ihi], $x) ) {
    my $istep = 1;
    for (;;) {
      $ilo = $ihi;
      $ihi = $ilo + $istep;
      if ( $ihi >= $num-1 ) {
	$ihi = $num - 1;
	last;
      }
      if ( &$LessThan($x, $sequenceRef->[$ihi]) ) {
	last;
      }
      $istep *= 2;
    }
  }

  # Now sequence(ilo) <= x < sequence(ihi).  Narrow the interval.
  for (;;) {
    # Find the middle point of the sequence.
    my $middle = int(($ilo + $ihi)/2);

    # The division above was integer, so if ihi = ilo+1, then
    # middle=ilo, which tests if x has been trapped.
    if ( $middle == $ilo ) {
      $last_interval_result = $ilo;
      return $ilo;
    }
    if ( &$LessThan($x, $sequenceRef->[$middle]) ) {
      $ihi = $middle;
    }
    else {
      $ilo = $middle;
    }
  }
}

1;

__END__

=pod

=head1 NAME

Math::IntervalSearch - Search where an element lies in a list of sorted elements

=head1 SYNOPSIS

 use Math::IntervalSearch qw(interval_search);
 my @array = (1..5);
 my $location = interval_search(2.4, \@array);

 # Use your own comparison operators.
 sub ReverseLessThan {
   $_[0] < $_[1];
 }

 sub ReverseLessThanEqualTo {
   $_[0] <= $_[1];
 }

 $location = interval_search(2.4,
                             \@array,
                             \&ReverseLessThan,
                             \&ReverseLessThanEqualTo);

=head1 DESCRIPTION

This subroutine is used to locate a position in an array of values where
a given value would fit.  It has been designed to be efficient in the
common situation that it is called repeatedly.  The user can supply a
different set of comparison operators to replace the standard < and <=.

=head1 SUBROUTINES

=over 4

=item B<interval_search> I<value> I<sequence> [I<less_than> [I<less_than_equal_to>]]

Given a I<value> I<interval_search> returns the location in the reference
to an array I<sequence> where the value would fit.  The default <
operator to compare the elements in I<sequence> can be replaced by the
subroutine I<less_than> which should return 1 if the first element passed
to I<less_than> is less than the second.  The default <= operator to
compare the elements in I<sequence> can be replaced by the subroutine
I<less_than> which should return 1 if the first element passed to
I<less_than> is less than the second.

The values in I<sequence> should already be sorted in numerically
increasing order or in the order that would be produced by using the
I<less_than> subroutine.

Let N be the number of elements in referenced array I<sequence>, then
I<interval_search> returns these values:
    -1  if                    I<value> < I<sequence>->[0]
    i   if I<sequence>->[i]   <= I<value> < I<sequence>->[i+1]
    N-1 if I<sequence>->[N-1] <= I<value>

If a reference is made to an empty array, then -1 is always returned.

If there is illegal input to I<interval_search>, such as an improper
number of arguments, then an empty list in list context, an undefined
value in scalar context, or nothing in a void context is returned.

This subroutine is designed to be efficient in the common situation
that it is called repeatedly, with I<value> taken from an increasing or
decreasing list of values.  This will happen, e.g., when an irregular
waveform is interpolated to create a sequence with constant separation.
The first guess for the output is therefore taken to be the value
returned at the previous call and stored in the variable ilo.  A first
check ascertains that ilo is less than the number of data points in
I<sequence>.  This is necessary since the present call may have nothing
to do with the previous call.  Then, if
    I<sequence>->[ilo] <= I<value> < I<sequence>->[ilo+1],

we set left = ilo and are done after just three comparisons.  Otherwise,
we repeatedly double the difference
    istep = ihi - ilo

while also moving ilo and ihi in the direction of x, until
    I<sequence>->[ilo] <= x < I<sequence>->[ihi],

after which bisection is used to get, in addition,
    ilo+1 = ihi.

Then left = ilo is returned.

=back 4

=head1 AUTHOR

Blair Zajac <bzajac@geostaff.com>.

=head1 COPYRIGHT

Copyright (c) 1998 by Blair Zajac.

=cut
