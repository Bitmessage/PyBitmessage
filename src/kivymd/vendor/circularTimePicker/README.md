Circular Date & Time Picker for Kivy
====================================

(currently only time, date coming soon)

Based on [CircularLayout](https://github.com/kivy-garden/garden.circularlayout).
The main aim is to provide a date and time selector similar to the
one found in Android KitKat+.

![Screenshot](screenshot.png)

Simple usage
------------

Import the widget with

```python
from kivy.garden.circulardatetimepicker import CircularTimePicker
```

then use it! That's it!

```python
c = CircularTimePicker()
c.bind(time=self.set_time)
root.add_widget(c)
```

in Kv language:

```
<TimeChooserPopup@Popup>:
    BoxLayout:
        orientation: "vertical"

        CircularTimePicker

        Button:
            text: "Dismiss"
            size_hint_y: None
            height: "40dp"
            on_release: root.dismiss()
```