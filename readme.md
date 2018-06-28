This repository holds custom components i wrote for [Home Assistant](https://www.home-assistant.io/).

I would like to create a pull request to add them as official components someday, but i do not have enough experience with python to meet all the requirements.

# Petpointer
[Petpointer](https://www.petpointer.ch) is a small pet tracker made in switzerland. They unfortunately don't offer a public API to request information about the current positions. This Component takes usage of an **unofficial** API which was reverse engineered from their web-platform.

## How to use
To use the component simply put the following configuration to your `configuration.yaml`.
```yaml
device_tracker:
  - platform: petpointer
    name: Java
    key: 35694XYZ4489230
    sec: a28e6ffa9b86eXYZ2ea92c298216d340
```
This configuration needs to be made for every tracker. If you happen to have multiple pets / trackers (just like me), your configuration looks like this:

```yaml
device_tracker:
  - platform: petpointer
    name: Java
    key: 35694XYZ4489230
    sec: a28e6ffa9b86eXYZ2ea92c298216d340

  - platform: petpointer
    name: Scala
    key: 356356XYZ933241
    sec: b2ea4e224a31XYZ6c1218a48eb54a471
```

## Getting the `key` and `sec` of your tracker

> The `key` and `sec` are different for every tracker, repeat the following steps for every pet.

1. Log in to your [Petpointer Dashboard](https://www.petpointer.ch/index.php?lang=de&page=100&pageId=100)
1. Switch to the pet you want to add to Home Assistant
1. Open the Developer Tools of your Browser (F12 for most browsers). 
1. Switch to the `Console` tab of the developer tools.
1. Enter the following code to the interactive javascript console
```javascript
var t=document.documentElement.innerHTML;var r=new RegExp(/inc\/pp-get-positions\.php\?lang=de&key=([^&]+)&sec=([^&]+)&id=([^&]+)/);var m=r.exec(t);console.log('key: '+m[1]+'\nsec: '+m[2]);
```
The script will return the `key` as well as the `sec` of your currently selected tracker. just insert them in the config together with the name of your pet, and you are good to go.