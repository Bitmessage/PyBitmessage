CircularLayout
==============

CircularLayout is a special layout that places widgets around a circle.

See the widget's documentation and the example for more information.

![Screenshot](screenshot.png)

size_hint
---------

size_hint_x is used as an angle-quota hint (widget with higher
size_hint_x will be farther from each other, and viceversa), while
size_hint_y is used as a widget size hint (widgets with a higher size
hint will be bigger).size_hint_x cannot be None.

Widgets are all squares, unless you set size_hint_y to None (in that
case you'll be able to specify your own size), and their size is the
difference between the outer and the inner circle's radii. To make the
widgets bigger you can just decrease inner_radius_hint.