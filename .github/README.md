# Chess to RSS

A simple script that allows you to get an RSS feed from a https://chess.com
user.

## Info

### What is in the RSS

The RSS feed contains all Chess games played by that user on https://chess.com.

### Potential uses

Using the RSS feed generated, you could automatically update a website to show
a feed of the Chess matches. You could also automatically send updates (such as
through a Discord server bot or via a notification) based on this RSS feed.

## Using

To use the `chesstorss.py` script, you will first need to (as usual) download
the script. Then, you make a `config.json` configuration file in the same directory 
that you are running the script (an example is provided in the `example/`
directory). Then, you simply run the script, which outputs a `.rss` file.

(*Here is the example of the `config.json`*)
```json
// you can find this at `example/config.example.json`
{
  "player": "your chess username",
  "optional": {
    "email": "(optional) your email",
    "rssOutput": "(optional) the output file (defaults to output/chess.rss)",
    "jsonOutput": "(optional) this is primarily used for testing, it doesn't default to anything"
  }
}
```

---

> [!NOTE]
> * The `player` configuration setting *must* be all lowercase.
> * The script assumes you have Python 3.12 or newer.
