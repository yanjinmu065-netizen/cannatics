import streamlit as st
import pandas as pd

st.title("📦 リキッド管理（一覧・編集・削除）")

# 📊 リキッドマスターのカラム定義（アプリの設定に合わせて適宜調整してください）
LIQUID_COLS = ["リキッド名", "配合詳細", "フレーバー", "ベース成分", "備考"]

# 1. データベースから最新のリキッド一覧を読み込む
df_liquid = load_data_from_db("Liquid_Master", LIQUID_COLS)

if df_liquid.empty:
    st.info("💡 まだ登録されているリキッドがありません。新規追加フォームから登録してください。")
else:
    st.subheader("🔍 登録済みリキッドの確認・操作")
    
    # 💡 1. 登録済みのリキッド一覧をプルダウン（セレクトボックス）にする
    liquid_options = df_liquid["リキッド名"].tolist()
    selected_liquid_name = st.selectbox("操作するリキッドを選択してください", liquid_options)
    
    # 選択されたリキッドのデータを取得
    selected_idx = df_liquid[df_liquid["リキッド名"] == selected_liquid_name].index[0]
    target_liquid = df_liquid.loc[selected_idx]
    
    st.markdown("---")
    st.write(f"### ✏️ 「{selected_liquid_name}」の詳細・編集")
    
    # 編集用入力フォーム（現在の値を初期値としてセット）
    edit_name = st.text_input("リキッド名", value=target_liquid.get("リキッド名", ""))
    edit_detail = st.text_area("配合詳細", value=target_liquid.get("配合詳細", ""))
    edit_flavor = st.text_input("フレーバー・香り", value=target_liquid.get("フレーバー", ""))
    
    # 💡 2. ボタンを小さく横並びにするために、横幅の狭いカラムを作成
    st.write("") # 少しスペースを空ける
    col_save, col_del, col_empty = st.columns([1.5, 1.2, 5])  # 比率を小さくすることでボタンが小さくなります
    
    # 💾 変更保存ボタン（小さめ）
    with col_save:
        save_btn = st.button("💾 変更を保存", key=f"save_{selected_idx}", use_container_width=True)
        
    # 🗑️ 削除ボタン（小さめ・赤色文字）
    with col_del:
        # 誤操作防止の確認チェックボックスを入れる場合はここに追加も可能です
        del_btn = st.button("🗑️ 削除", key=f"del_{selected_idx}", use_container_width=True)
        
    # ーーー ボタン押下時の処理 ーーー
    if save_btn:
        try:
            # DataFrameのデータを上書き
            df_liquid.at[selected_idx, "リキッド名"] = edit_name.strip()
            df_liquid.at[selected_idx, "配合詳細"] = edit_detail.strip()
            df_liquid.at[selected_idx, "フレーバー"] = edit_flavor.strip()
            
            # 全体保存
            if save_all_data_to_db("Liquid_Master", df_liquid, LIQUID_COLS):
                st.success(f"🎉 「{edit_name}」の変更を保存しました！")
                st.rerun()
        except Exception as e:
            st.error(f"❌ 保存中にエラーが発生しました: {e}")
            
    if del_btn:
        try:
            # 指定行を削除してインデックスをリセット
            df_liquid = df_liquid.drop(selected_idx).reset_index(drop=True)
            
            # 全体保存
            if save_all_data_to_db("Liquid_Master", df_liquid, LIQUID_COLS):
                st.warning(f"🗑️ 「{selected_liquid_name}」を一覧から削除しました。")
                st.rerun()
        except Exception as e:
            st.error(f"❌ 削除中にエラーが発生しました: {e}")
