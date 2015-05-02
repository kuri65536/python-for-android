* [Report issue](../README.md#create_issue)

Tips: Install Android NDK
===
How to install a cross-compiler toolchain for Android.

Download the NDK from Android.
---
* Download the [NDK from Android](http://developer.android.com/sdk/ndk/index.html).
* Install. (typically would be in ~/android-ndk-r5 or similar)

```shell
export ANDROID_NDK=~/android-ndk-r5
export ANDROID_NDK_TOOLCHAIN_ROOT=~/android-toolchain
$ANDROID_NDK/build/tools/make-standalone-toolchain.sh --platform=android-9
--install-dir=$ANDROID_NDK_TOOLCHAIN_ROOT
```

_NB: The ~ does not expand to your home folder in --install-dir.
That's why I've put it in a shell variable, which we're going to be using later anyway._

I picked the latest platform as an example, but anything reasonably sensible will do.

You can find more detail by looking in
$ANDROID\_NDK/docs/STANDALONE-TOOLCHAIN.html. (Why it's not
available directly on the web, I have no idea)

I have only been able to get this working under Linux. In theory it ought to work for Windows with
Cygwin installed, but so far it's not looking good.

<!---
 vi: ft=markdown
 -->
