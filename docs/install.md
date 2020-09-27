# インストール￹方法￺ほうほう￻

※ インストールにあたっては、さきに「[ひらがなIME](https://github.com/esrille/ibus-hiragana)」をインストールしておく￹必要￺ひつよう￻があります。

<br>

　つかっているOSが、Fedora, Ubuntu, Raspberry Pi OSのどれかであれば、インストール￹用￺よう￻のソフトウェア パッケージを「[Releases](https://github.com/esrille/typing-practice/releases)」ページからダウンロードできます。

## じぶんでビルドする￹方法￺ほうほう￻

　「タイピングの￹練習￺れんしゅう￻」をじぶんでビルドしてインストールしたいときは、つぎの￹手順￺てじゅん￻でインストールできます。

```
git clone https://github.com/esrille/typing-practice.git
./autogen.sh
make
sudo make install
```
