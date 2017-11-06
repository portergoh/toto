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
**Update the cache with the latest results from Singapore Pool**
<br>toto_analyzer.py --update
<br>
<br>**Fetch the last drawn 5 results**
<br>toto_analyzer.py -d 5
```
  Thu, 02 Nov 2017 - 7 17 18 30 32 47
  Mon, 30 Oct 2017 - 8 20 30 43 46 48
  Thu, 26 Oct 2017 - 3 10 25 32 36 37
  Mon, 23 Oct 2017 - 2 9 23 35 38 48
  Thu, 19 Oct 2017 - 2 4 15 20 26 28
```
**Generate a num cloud plot based on all last 15 draws**
<br>toto_analyzer.py -d 15 --plotfreq
<p align="center">
  <img src="../master/resource/numcloud.png" width="500"/>
</p>
