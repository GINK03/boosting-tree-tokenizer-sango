# 勾配ブースティングを利用した教師あり分かち書き

C++用のモデル（データを入力すると、結果が返ってくるもの）が構築できるので、任意の言語、例えばRuby等でも分かち書きを利用できる様になります  


## 理論

## 前処理
githubのレポジトリには最初から学習済みのデータを用意していますが、自分で必要なデータを学習させる場合には以下のステップで行います  

教師あり分かち書きなので、教師となる分かち書きの粒度を示したデータセットが必要となる  
例えば、mecabの生成する分かち書きを教師データとする例です  

映画.com様から取得した500MByte程度の映画のレビューデータを利用して、boosting-tree-tokenizerに学習させるデータセットを作成します  

ダウンロード(20GByte程度あります)
```console
$ cd misc
$ python3 downloader.py 
```

#### 1. ポジティブデータ、ネガティブデータセットの作成

以下の様なデータを作成します  

**ポジティブ**  
\[、今日は o 天気がい\]  
分かち書きがあり得る箇所にoが入ります  
**ネガティブ**  
\[ベネチア x ンマスク\]  
分かち書きとしてありえないところにxが入ります  

#### 2. スパースマトリックスの作成
特徴量の作り方として、周辺の単語とその距離の二つの軸で独立な特徴量とするため、まともにやろうとすると、大変高次元化して今います.  
そのため、スパースマトリックスとして表現するために、まず、特徴量に対してユニークなインデックスを付与します  
```console
$ python3 wakati.py --make_sparse
```
付与したインデックスをもとに、スパースマトリックスを組み立てます  
```console
$ python3 wakati.py --make_sparse2 
```

#### 3. train, testデータの作成
お使いのマシンのスペックに依存しますが、trainデータで100万, testデータで10万データセットを利用する際には、この様にしまします  
```console
$ head -n 1000000 ./misc/download/dataset.txt > train
$ tail -n 100000 ./misc/download/dataset.txt > test
```

## LightGBMでの学習
binary-classificationでの二値分類の問題としてみなします  
具体的には、ある文字と文字の間に、分かち書きすべきかどうかの確率値を計算します  
50%を超えると、分かち書きを有効にし、50%未満では分かち書きを行いません  

有名な勾配ブースティングライブラリにはXGBoostとLightGBMとCatBoostなどがあるのですが、スパースマトリックスの扱いやすさからLightGBMを使います  

### 1. LightGBMのインストール  
cmakeでビルドとインストールできます（要：GNU make, gcc, cmake）
```console
$ git clone https://github.com/Microsoft/LightGBM
$ cd LightGBM
$ mkdir build
$ cd build
$ cmake ..
$ make -j16
$ sudo make install
```
これでlightgbmコマンドがシステムに追加されました  

### 2. LightGBMで学習する
学習に使うパラメータを記述したconfがあるので、必要に応じでパラメータを変更して用いてください  
```console
$ lightgbm config=train.conf
```

## 学習したモデルで分かち書きをしてみる  

映画.comさんのレビューをランダムサンプルして適当に分かち書きしてみています  
```console
$ python3 intractive.py --test
```
出力はこの様になり、概ね、期待通りの分かち書きになっていることが確認できるかと思います  
```console
調子/に/乗り/過ぎ/て/いる/感/が/嫌い/だ/が/、/この/作品/は/見/て/よかっ/た
はじめ/と/する/役者/さん/たち/の/演技/に/泣か/さ/れ/た/。/小林武史/の/音楽/も/素晴らしく/て/サントラ/を/買っ/て/しまっ/た/。/原作/も/読み/た
読ん/で/で/、/これ/を/見/た/が/とく/に/違和感/なく/見れ/た/。/多分/、/原作/は/もっと/色々命/と/の/引き換え/を/考え/て/た/気/も/する/けど/、/これ/は/これ/で/よい/。
映画/は/苦手/だっ/た/の/です/が/、/母/の/誘い/で/見/に/行き/まし/た/。/後半部分/が/良い/です/。/自分/で/も/なん/で/泣い/て/いる/か分から/ない/ほど/涙/が/出まし/た/。
/目/が/真っ赤/だ/けど/大丈夫/？/！/と/言わ/れ/まし/た/.../。/今/に/なっ/て/、/あぁ/良い/映画/だっ/た/。/と/思っ/た/ので/レビュー/し/て/み/まし/た/。/命より/大切/な/もの/は/あり/ます/。
スケジュール/が/合わ/なく/て/見/に/行け/なかっ/た/が/、/近場/の/IMAX上映館/が/今週末/から/箱割/を/大幅/に/カット/する/こと/が/わかり/、/慌て/て/見/に/行っ/た/。/IMAX上映/を/前提/と/し/た/映像/
は/凄い/迫力/と/臨場感/だっ/た/が/、/人物/や/物語/は/平板/な/もので/、/特別/感動/も/なく/終了/。/欧州戦史/に対する/ある/程度/の/前提/知識/が/必要/だっ/た/の/かも/しれ/ない/と/思っ/て/パンフ/を/購
入し/た/が/、/これ/が/凄い/情報量/だっ/た/。
```

## Pure C++で辞書なしで形態素解析する

### feature_index.pklのc++化
pickle形式の特徴量の対応表はc++には読めないので、cppのファイルに変換します  
```console
$ python3 intractive.py --make_cpp
```

## ライセンス　
MIT
