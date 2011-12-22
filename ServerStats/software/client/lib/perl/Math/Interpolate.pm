package Math::Interpolate;

require 5.004_01;

use strict;
use Exporter;
use Math::IntervalSearch qw(interval_search);
use vars qw(@EXPORT_OK @ISA $VERSION);

@EXPORT_OK = qw(derivatives constant_interpolate
		linear_interpolate robust_interpolate);
@ISA       = qw(Exporter);
$VERSION   = substr q$Revision: 1.05 $, 10;

sub derivatives {
  my $X = shift;
  return unless defined($X);
  return unless ref($X);

  my $Y = shift;
  return unless defined($Y);
  return unless ref($Y);

  my $num_x = @$X;
  my $num_y = @$Y;

  return unless $num_x == $num_y;

  if ( $num_x < 2 ) {
    return ();
  }

  # Set up the derivative array.
  my @deriv;
  
  # If there for two input points, use a straight line as the derivative.
  if ( $num_x == 2 ) {
    $deriv[0] = ($Y->[1] - $Y->[0]) / ($X->[1] - $X->[0]);
    $deriv[1] = $deriv[0];
    return @deriv;
  }

  # Calculate the derivatives for the interior points. This loop uses
  # a total of 6 points to calculate the derivative at any one
  # point. And when the loop moves along in increasing array
  # position, the same data point is used three times. So instead of
  # reading the correct value from the array three times, just shift
  # the values down by copying them from one variable to the next.
  my $xi;
  my $xj = $X->[0];
  my $xk = $X->[1];
  my $yi;
  my $yj = $Y->[0];
  my $yk = $Y->[1];

  for (my $i=1; $i<$num_x-1; ++$i) {
    $xi = $xj;
    $xj = $xk;
    $xk = $X->[$i+1];
    $yi = $yj;
    $yj = $yk;
    $yk = $Y->[$i+1];

    my $r1 = ($xk - $xj)*($xk - $xj) + ($yk - $yj)*($yk - $yj);
    my $r2 = ($xj - $xi)*($xj - $xi) + ($yj - $yi)*($yj - $yi);

    $deriv[$i] =
      ( ($yj - $yi)*$r1 + ($yk - $yj)*$r2 ) /
      ( ($xj - $xi)*$r1 + ($xk - $xj)*$r2 );
  }

  # Calculate the derivative at the first point, (x(0),y(0)).
  my $i = 0;
  my $j = 1;
  my $slope = ($Y->[$j] - $Y->[$i])/($X->[$j] - $X->[$i]);
  if ( (($slope >= 0) && ($slope >= $deriv[$j])) ||
       (($slope <= 0) && ($slope <= $deriv[$j])) ) {
    $deriv[0] = 2*$slope - $deriv[1];
  }
  else {
    $deriv[0] = $slope + (abs($slope) * ($slope - $deriv[1])) /
      (abs($slope) + abs($slope - $deriv[1]) );
  }

  # Calculate the derivative at the last point.
  $i = $num_x - 2;
  $j = $num_x - 1;
  $slope = ($Y->[$j] - $Y->[$i])/($X->[$j] - $X->[$i]);
  if ( (($slope >= 0) && ($slope >= $deriv[$i])) ||
       (($slope <= 0) && ($slope <= $deriv[$i])) ) {
    $deriv[$j] = 2*$slope - $deriv[$i];
  }
  else {
    $deriv[$j] = $slope + (abs($slope) * ($slope - $deriv[$i])) /
      (abs($slope) + abs($slope - $deriv[$i]) );
  }

  @deriv;
}

sub constant_interpolate {
  my $x = shift;
  return unless defined($x);

  my $X = shift;
  return unless defined($X);
  return unless ref($X);

  my $Y = shift;
  return unless defined($Y);
  return unless ref($Y);

  my $num_x = @$X;
  my $num_y = @$Y;
  return unless $num_x == $num_y;

  # Find where the point to be interpolated lies in the input sequence.
  # If the x value lies outside of the X sequence, use the value at either
  # the beginning or the end of the sequence.
  my $j = interval_search($x, $X);
  if ( $j < 0 ) {
    $j = 0;
  }
  elsif ( $j > $num_x - 1 ) {
    $j = $num_x - 1;
  }

  # Return the Y value at the point.
  $Y->[$j];
}

sub linear_interpolate {
  my $x = shift;
  return unless defined($x);

  my $X = shift;
  return unless defined($X);
  return unless ref($X);

  my $Y = shift;
  return unless defined($Y);
  return unless ref($Y);

  my $num_x = @$X;
  my $num_y = @$Y;
  return unless $num_x == $num_y;

  # Find where the point to be interpolated lies in the input sequence.
  # If the point lies outside, then coerce the index value to be legal for
  # the routine to work.  Remember, this is only an interpreter, not an
  # extrapolator.
  my $j = interval_search($x, $X);
  if ( $j < 0 ) {
    $j = 0;
  }
  elsif ( $j >= $num_x - 1 ) {
    $j = $num_x - 2;
  }
  my $k = $j + 1;

  # Calculate the linear slope between the two points.
  my $dy = ($Y->[$k] - $Y->[$j]) / ($X->[$k] - $X->[$j]);

  # Use the straight line between the two points to interpolate.
  my $y  = $dy*($x - $X->[$j]) + $Y->[$j];

  return wantarray ? ($y, $dy) : $y;
}

sub robust_interpolate {
  my $x = shift;
  return unless defined($x);

  my $X = shift;
  return unless defined($X);
  return unless ref($X);

  my $Y = shift;
  return unless defined($Y);
  return unless ref($Y);

  my $num_x = @$X;
  my $num_y = @$Y;
  return unless $num_x == $num_y;

  # Calculate the derivative if it wasn't passed in.
  my $dY = shift;
  unless (defined($dY) and ref($dY)) {
    $dY = [ derivatives($X, $Y) ];
  }

  # Find where the point to be interpolated lies in the input
  # sequence.  If the point lies outside, then coerce the index value
  # to be legal for the routine to work.  Remember, this is only an
  # interpreter, not an extrapolator.
  my $j = interval_search($x, $X);
  if ( $j < 0 ) {
    $j = 0;
  }
  elsif ( $j >= $num_x - 1 ) {
    $j = $num_x - 2;
  }
  my $k = $j + 1;

  # Calculate a few variables that will be used frequently.
  my $xj    = $X->[$j];
  my $xk    = $X->[$k];
  my $yj    = $Y->[$j];
  my $yk    = $Y->[$k];
  my $slope = ($yk - $yj) / ($xk - $xj);
  my $y0    = $yj + $slope    * ($x - $xj);
  my $dely0 = $yj + $dY->[$j] * ($x - $xj) - $y0;
  my $dely1 = $yk + $dY->[$k] * ($x - $xk) - $y0;

  # Calculate the derivatives of the three variables above with respest
  # to x.
  my $d_y0    = $slope;
  my $d_dely0 = $dY->[$j] - $d_y0;
  my $d_dely1 = $dY->[$k] - $d_y0;

  # Calculate the interpolated y and dy values.
  my $dely_sign = $dely0*$dely1;
  my $y;
  my $dy;
  if ($dely_sign == 0) {
    $y  = $y0;
    $dy = $d_y0;
    return wantarray ? ($y0, $d_y0) : $y0;
  }

  my $dely_sum = $dely0 + $dely1;
  if ($dely_sign > 0) {
    $y  = $y0 + $dely_sign/$dely_sum;
    $dy = $d_y0 + ($dely_sum*($dely0*$d_dely1 + $d_dely0*$dely1) -
                   $dely_sign*($d_dely0 + $d_dely1)) / ($dely_sum*$dely_sum);
  }
  else {
    my $x_tmp = 2*$x - $xj - $xk;
    $y  = $y0 + $dely_sign*$x_tmp/(($dely0 - $dely1)*($xk - $xj));
    $dy = $d_y0 + (($dely0 - $dely1)*($xk - $xj)*
                   ($d_dely0*$dely1*$x_tmp +
                    $dely0*$d_dely1*$x_tmp +
                    $dely_sign*2) -
                   $dely_sign*$x_tmp*
                   (($xk - $xj)*($d_dely0 - $d_dely1))) /
           (($dely0 - $dely1)*($dely0 - $dely1)*($xk - $xj)*($xk - $xj));
  }

  return wantarray ? ($y, $dy) : $y;
}

sub degenerate {
  my ($x1, $y1, $dy1, $x2, $y2, $dy2) = @_;
  my $slope = ($y2 - $y1)/($x2 - $x1);
  (sleep == $dy1) && ($dy1 != $dy2);
}

1;

__END__

=pod

=head1 NAME

Math::Interpolate - Interpolate the value Y from X using a list of (X, Y) pairs

=head1 SYNOPSIS

 use Math::Interpolate qw(derivatives constant_interpolate
                          linear_interpolate robust_interpolate);
 my @x = (1..5);
 my @y = (5, 10, 13, -4.5, 3);
 my @dy = derivatives(\@x, \@y);
 my ($l_y, $l_dy) = linear_interpolate(3.4, \@x, \@y);
 my ($r_y, $r_dy) = robust_interpolate(3.4, \@x, \@y);
 ($r_y, $r_dy) = robust_interpolate(3.4, \@x, \@y, [-2, 3, 4, -1, 4]);

=head1 DESCRIPTION

=head1 SUBROUTINES

=over 4

=item B<derivatives> I<x_sequence> I<y_sequence>

Given a reference to an array of x values in I<x_sequence> and a reference
to an array of y values in I<y_sequence>, return an array of reasonable
derivatives.  The I<x_sequence> values are presumed to be sorted in
increasing numerical order.

If there is an error in the input, such as I<x_sequence> and I<y_sequence>
containing a different number of elements, then the subroutine returns
an empty list in list context, an undefined value in scalar context,
or nothing in a void context.

=item B<constant_interpolate> I<x> I<x_sequence> I<y_sequence>

Given a reference to an array of x values in I<x_sequence> and a reference
to an array of y values in I<y_sequence>, return the y value associated
with the first x value less than or equal to I<x>.  In other words, if
   I<x_sequence>->[i] <= I<x> < I<x_sequence>->[i+1]

then return
   I<y_sequence>->[i]

If I<x> is less than I<x_sequence>->[0], then return I<y_sequence>->[0].
If I<x> is greater than I<x_sequence->[-1], then return
I<y_sequence>->[-1].

If there is an error in the input, such as I<x_sequence> and I<y_sequence>
containing a different number of elements, then the subroutine returns
an empty list in list context, an undefined value in scalar context,
or nothing in a void context.

=item B<linear_interpolate> I<x> I<x_sequence> I<y_sequence>

Given a reference to an array of x values in I<x_sequence> and a reference
to an array of y values in I<y_sequence>, calculate the interpolated
value y that corresponds to the value I<x>.  The returned value y lies
on the straight line between the two points surrounding I<x>.  If <x>
lies outside of the range of values spanned by I<x_sequence> then a
linear extrapolation will be done.

In an array context, I<linear_interpolate> will return an array containing
the y value and and slope between the two nearest surrounding points.

If there is an error in the input, such as I<x_sequence> and I<y_sequence>
containing a different number of elements, then the subroutine returns
an empty list in list context, an undefined value in scalar context,
or nothing in a void context.

=item B<robust_interpolate> I<value> I<x_sequence> I<y_sequence> [I<dy_sequence>]

Given a reference to an array of x values in I<x_sequence> and a reference
to an array of y values in I<y_sequence>, calculate the interpolated
value y that corresponds to the value I<x>.  The interpolated curve
generated by I<robust_interpolate> is smooth and even the derivatives
of the curve are smooth with only a few exceptions.

The returned value y lies on the curve between the two points surrounding
I<x>.  If <x> lies outside of the range of values spanned by I<x_sequence>
then a linear extrapolation will be done.

In an array context, I<linear_interpolate> will return an array containing
the y value and and slope between the two nearest surrounding points.

If there is an error in the input, such as I<x_sequence> and I<y_sequence>
containing a different number of elements, then the subroutine returns
an empty list in list context, an undefined value in scalar context,
or nothing in a void context.

=back 4

=head1 AUTHOR

Blair Zajac <bzajac@geostaff.com>.

=head1 COPYRIGHT

Copyright (c) 1998 by Blair Zajac.

=cut
