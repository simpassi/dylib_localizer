# What!
It's a dylib dependency localizer

# Why!
Sometimes you just need to ship something with a command-line tool and the only way to do that in time is to pull it using something like conda or brew or similar, and they come with a plethora of dependencies. It's not the prettiest, but they'll work if you also ship the dylib dependencies but that requires some @rpath rewriting and recursive dependency scanning.

# How!
Just go to the folder where the executable is, and type:
```shell
localize.py my_executable
```

It'll pull down all the dylib dependencies into a "lib" folder and make the executable look for them in a relative path.
