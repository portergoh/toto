## TOTO analyzer for Singapore Pool v1.0
This is a tool developed as part of the **Python for Data, Ops and Things** course.<br>
It collect and analyse data from Singapore pool.

```
usage: toto_analyzer.py [-h] [--plotfreq] [--update] [-d DRAW] [-s SET]
                        [-qp QUICKPICK]

optional arguments:
  -h, --help            show this help message and exit
  --plotfreq            plot number frequency using word cloud
  --update              update local cache with latest records from Singapore
                        Pool
  -d DRAW, --draw DRAW  return list of last draws based on user input
  -s SET, --set SET     return sets of random numbers, use together with -qp
                        option
  -qp QUICKPICK, --quickpick QUICKPICK
                        generate a list of random numbers
```

### Examples
Fetch the last drawn result
toto_analyzer.py -d 1
```
Thu, 02 Nov 2017 - 7 17 18 30 32 47
```
