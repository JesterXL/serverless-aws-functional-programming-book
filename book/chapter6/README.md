# Parsing Mass Data

We need various mass data for our asteroids and exoplanets to calculate various other things like value. Many of the known ones have their masses documented. We're going to parse that data, convert to JSON, and re-use later when we merge all this data together in a database. Unlike others, we'll bake this data into the Lambda itself. It doesn't update often so doing a code deploy to update it is justifiable.

It looks like this:

```
 1 Ceres 9.55E+20 4.38E+19
 1 Ceres 9.54E+20 1.69E+19
 1 Ceres 9.19E+20 1.41E+19
 1 Ceres 9.29E+20 1.79E+19
 1 Ceres 9.52E+20 7.76E+18
 1 Ceres 9.47E+20 4.57E+18
```

And correlates to the designation. Ceres is a [beast of an asteroid](https://en.wikipedia.org/wiki/Ceres_(dwarf_planet)), btw. Cat is 580 miles / 940 km in diameter! 

<img src="./Ceres_-_RC3_-_Haulani_Crater_(22381131691)_(cropped).jpg"></img>