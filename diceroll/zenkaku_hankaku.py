# diceroll/zenkaku_hankaku.py

def zenkaku_to_hankaku():
    zenkaku = "０１２３４５６７８９ｄＤｂＢｃＣ＋－＊／＝＞＜（）［］，　"
    hankaku = "0123456789dDbBcC+-*/=><()[], "
    return str.maketrans(zenkaku, hankaku)
