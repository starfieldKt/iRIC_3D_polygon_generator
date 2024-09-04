import iric
import sys
import numpy as np
from stl import mesh

# 格子点の座標読み込み
# --------------------------------------------------
# メモ
# --------------------------------------------------
# CGNSから読み込む時は1次元配列、順番は以下
# --------------------------------------------------
#      j
#      ↑
#     4| 24, 25, 26, 27, 28, 29
#     3| 18, 19, 20, 21, 22, 23
#     2| 12, 13, 14, 15, 16, 17
#     1|  6,  7,  8,  9, 10, 11
#     0|  0,  1,  2,  3,  4,  5
#       ----------------------- →　i
#         0   1   2   3   4   5
# --------------------------------------------------

# --------------------------------------------------
# 書き込みと読み込み用CGNSファイルを開く
# --------------------------------------------------
def cgns_open():

    global write_cgns_id
    global read_cgns_id

    write_cgns_id = iric.cg_iRIC_Open(write_cgns_name, iric.IRIC_MODE_MODIFY)

    read_cgns_name = iric.cg_iRIC_Read_String(write_cgns_id, "read_cgns_name")
    read_cgns_id = iric.cg_iRIC_Open(read_cgns_name, iric.IRIC_MODE_READ)


# --------------------------------------------------
# 書き込みと読み込み用CGNSファイルを閉じる
# --------------------------------------------------
def cgns_close():
    iric.cg_iRIC_Close(read_cgns_id)
    iric.cg_iRIC_Close(write_cgns_id)


# --------------------------------------------------
# 初期条件等を読み込む
# --------------------------------------------------
def read_initial_condition():

    global n_step_read, elevation_scale, save_location, save_file_name, n_cell
    global start_time_output, end_time_output
    global output_stl, output_obj
    global bottom_elevation_name
    global add_water_surface, ws_elevation_name
    global n_node_x, n_node_y, coordinate_x, coordinate_y
    global coordinate_x_1d, coordinate_y_1d
    global inversion_stl, inversion_obj

    # 読み込み用CGNSの計算ステップ数
    n_step_read = iric.cg_iRIC_Read_Sol_Count(read_cgns_id)
    # 3Dモデルを出力を終了する時間
    elevation_scale = iric.cg_iRIC_Read_Real(write_cgns_id, "elevation_scale")

    # 読み込み用CGNSの標高のデータ名
    bottom_elevation_name = iric.cg_iRIC_Read_String(
        write_cgns_id, "bottom_elevation_name"
    )

    # 水面を追加するか
    add_water_surface = iric.cg_iRIC_Read_Integer(write_cgns_id, "add_water_surface")
    # 読み込み用CGNSの水面標高のデータ名
    ws_elevation_name = iric.cg_iRIC_Read_String(write_cgns_id, "ws_elevation_name")

    # stlを出力するか
    output_stl = iric.cg_iRIC_Read_Integer(write_cgns_id, "output_stl")
    # stlの南北を反転させるか
    inversion_stl = iric.cg_iRIC_Read_Integer(write_cgns_id, "inversion_stl")
    # objを出力するか
    output_obj = iric.cg_iRIC_Read_Integer(write_cgns_id, "output_obj")
    # objの南北を反転させるか
    inversion_obj = iric.cg_iRIC_Read_Integer(write_cgns_id, "inversion_obj")

    # ファイルの保存場所
    save_location = iric.cg_iRIC_Read_String(write_cgns_id, "save_location")
    # 保存するファイル名
    save_file_name = iric.cg_iRIC_Read_String(write_cgns_id, "save_file_name")

    # 3Dモデルを出力を開始する時間
    start_time_output = iric.cg_iRIC_Read_Real(write_cgns_id, "start_time_output")
    # 3Dモデルを出力を終了する時間
    end_time_output = iric.cg_iRIC_Read_Real(write_cgns_id, "end_time_output")
    # 構造格子の格子点数
    n_node_x, n_node_y = iric.cg_iRIC_Read_Grid2d_Str_Size(read_cgns_id)
    # 格子点の座標を読み込み
    coordinate_x, coordinate_y = iric.cg_iRIC_Read_Grid2d_Coords(read_cgns_id)
    # セルの数を読み込み
    n_cell = iric.cg_iRIC_Read_Grid_CellCount(read_cgns_id)

    # CGNSから読み込んだcoordinate_xとcoordinate_yをnumpy配列にする。
    coordinate_x_1d = np.array(coordinate_x)
    coordinate_y_1d = np.array(coordinate_y)

    # CGNSから読み込んだcoordinate_x_1dとcoordinate_y_1dは1次元配列なので2次元配列にする(デバッグ用)
    coordinate_x_2d = np.array(coordinate_x_1d).reshape(n_node_y, n_node_x)
    coordinate_y_2d = np.array(coordinate_y_1d).reshape(n_node_y, n_node_x)


# --------------------------------------------------
# 河床の水面の標高を読み込む。(河床)
# --------------------------------------------------
def read_elevation_vale_bottom():

    global bottom_elevation_vale_1d

    bottom_elevation_vale = iric.cg_iRIC_Read_Sol_Node_Real(
        read_cgns_id, step, bottom_elevation_name
    )
    # CGNSから読み込んだelevation_valeをnumpy配列にする。
    bottom_elevation_vale_1d = np.array(bottom_elevation_vale) * elevation_scale

    # CGNSから読み込んだelevation_valeは1次元配列なので2次元配列にする(デバッグ用)
    bottom_elevation_vale_2d = np.array(bottom_elevation_vale_1d).reshape(
        n_node_y, n_node_x
    )


# --------------------------------------------------
# 水面の標高を読み込む。(水面)
# --------------------------------------------------
def read_elevation_vale_ws():

    global ws_elevation_vale_1d

    ws_elevation_vale = iric.cg_iRIC_Read_Sol_Node_Real(
        read_cgns_id, step, ws_elevation_name
    )
    # CGNSから読み込んだws_elevation_valeをnumpy配列にする。
    ws_elevation_vale_1d = np.array(ws_elevation_vale) * elevation_scale

    for i in range(n_node_x * n_node_y):
        if ws_elevation_vale_1d[i] <= bottom_elevation_vale_1d[i]:
            ws_elevation_vale_1d[i] = bottom_elevation_vale_1d[i]

    # CGNSから読み込んだelevation_valeは1次元配列なので2次元配列にする(デバッグ用)
    ws_elevation_vale_2d = np.array(ws_elevation_vale_1d).reshape(n_node_y, n_node_x)


def get_v(x_coords, y_coords, z_coords):
    """
    x, y, z座標値を含む二次元配列からobjの頂点情報を取得する。\n
    Args:
        x_coords : x座標の一次元配列
        y_coords : y座標の一次元配列
        z_coords : z座標の一次元配列
    Returns:
        v_text : obj形式の頂点情報
    """

    v_text = ""

    # テキスト情報として取得(objはyが高さ方向)
    for i in range(x_coords.shape[0]):
        v_text += (
            "v "
            + str(x_coords[i])
            + " "
            + str(z_coords[i])
            + " "
            + str(y_coords[i] * (1 - 2 * inversion_obj))
            + "\n"
        )

    return v_text


def get_vt(x_coords, y_coords):
    """
    x,y座標値を含む二次元配列からテクスチャ座標情報を取得する。\n
    Args:
        x_coords : x座標の二次元配列
        y_coords : y座標の二次元配列
    Returns:
        vt_text : obj形式のテクスチャ座標情報
    """
    # 戻り値の定義
    vt_text = ""

    # 最大値&最小値の取得
    x_min = min(x_coords)
    x_max = max(x_coords)
    y_min = min(y_coords)
    y_max = max(y_coords)

    for i in range(x_coords.shape[0]):
        # テクスチャ座標
        xt = (x_coords[i] - x_min) / (x_max - x_min)
        yt = (y_coords[i] - y_min) / (y_max - y_min)

        # テクスチャ座標の定義
        vt_text += "vt " + str(xt) + " " + str(yt) + "\n"

    return vt_text


def get_f(triangle_configuration_node_list):
    """
    格子形状からobjのメッシュ情報を取得する。\n
    Args:
        ni : 縦断方向の分割数
        nj : 横断方向の分割数
    Returns:
        f_text : obj形式のメッシュ情報
    """
    # 戻り値の定義
    f_text = ""

    for i in range(triangle_configuration_node_list.shape[0]):

        f_text += (
            "f "
            + str(triangle_configuration_node_list[i][0] + 1)
            + "/"
            + str(triangle_configuration_node_list[i][0] + 1)
            + "/"
            + "1"
            + " "
            + str(triangle_configuration_node_list[i][1] + 1)
            + "/"
            + str(triangle_configuration_node_list[i][1] + 1)
            + "/"
            + "1"
            + " "
            + str(triangle_configuration_node_list[i][2] + 1)
            + "/"
            + str(triangle_configuration_node_list[i][2] + 1)
            + "/"
            + "1"
            + "\n"
        )

    return f_text


# --------------------------------------------------
# 三角形分割
# --------------------------------------------------
def make_tryangle(previous_count):

    triangle_configuration_node_list_tmp = np.full((n_cell * 2, 3), 0)

    for i in range(n_node_x - 1):
        for j in range(n_node_y - 1):

            tryangle_tmp_1 = np.array(
                [
                    i + j * n_node_x + previous_count,
                    (i + 1) + j * n_node_x + previous_count,
                    (i + 1) + (j + 1) * n_node_x + previous_count,
                ],
                dtype=np.int64,
            )
            tryangle_tmp_2 = np.array(
                [
                    i + j * n_node_x + previous_count,
                    (i + 1) + (j + 1) * n_node_x + previous_count,
                    i + (j + 1) * n_node_x + previous_count,
                ],
                dtype=np.int64,
            )

            triangle_configuration_node_list_tmp[
                (i + j * (n_node_x - 1)) * 2
            ] = tryangle_tmp_1
            triangle_configuration_node_list_tmp[
                (i + j * (n_node_x - 1)) * 2 + 1
            ] = tryangle_tmp_2

    return triangle_configuration_node_list_tmp


# --------------------------------------------------
# stlファイルの作成
# --------------------------------------------------
def make_polygon_stl(elevation_vale_1d, triangle_configuration_node_list, bottom_or_ws):

    polygon_node_list = np.stack(
        [
            coordinate_x_1d,
            coordinate_y_1d * (1 - 2 * inversion_stl),
            elevation_vale_1d,
        ],
        1,
    )

    # この辺についてはよくわかっていない
    polygon_obj = mesh.Mesh(
        np.zeros(triangle_configuration_node_list.shape[0], dtype=mesh.Mesh.dtype)
    )
    polygon_obj.remove_duplicate_polygons = True

    for i, f in enumerate(triangle_configuration_node_list):
        for j in range(3):
            polygon_obj.vectors[i][j] = polygon_node_list[f[j], :]

    polygon_obj.save(
        save_location
        + "\\"
        + save_file_name
        + "_time="
        + str("{:.2f}".format(time))
        + "_"
        + bottom_or_ws
        + ".stl"
    )


def make_polygon_obj(v_text, vt_text, f_text, bottom_or_ws):
    # objファイル
    with open(
        save_location
        + "\\"
        + save_file_name
        + "_time="
        + str("{:.2f}".format(time))
        + "_"
        + bottom_or_ws
        + ".obj",
        "w",
    ) as f:

        # マテリアル定義ファイル
        obj_text = "# mtl file" + "\n"
        obj_text += "mtllib " + "texture" + "_" + bottom_or_ws + ".mtl" + "\n" + "\n"

        # # グループ名
        # obj_text += "# Group Name" + "\n"
        # obj_text += "g step" + str(step) + "\n" + "\n"

        # MAT
        obj_text += "# Material Infomation" + "\n"
        obj_text += "usemtl water" + "\n" + "\n"

        # 格子点情報
        obj_text += "# Node Coordinate" + "\n"
        obj_text += v_text + "\n"

        # テクスチャ座標情報
        obj_text += "# Texture Coordinate" + "\n"
        obj_text += vt_text + "\n"

        # 垂直方向情報
        obj_text += "# Vertical Infomation" + "\n"
        obj_text += "vn 0.0 1.0 0.0" + "\n" + "\n"

        # メッシュ情報
        obj_text += "# Mesh Infomaition" + "\n"
        obj_text += f_text

        # 書き込み
        f.write(obj_text)


if __name__ == "__main__":

    ier = 0

    if len(sys.argv) < 2:
        print("Error: CGNS file name not specified.")
        exit()

    write_cgns_name = sys.argv[1]

    # write_cgns_name = (
    #     "C:\WorkSpace\iRIC\iRICver4\project\stl_generator_test\polygon_gen_3\Case1.cgn"
    # )

    cgns_open()
    read_initial_condition()

    for step_tmp in range(n_step_read):

        # python は0からスタートなので1足しておく
        step = step_tmp + 1

        # 時間を読み込む
        time = iric.cg_iRIC_Read_Sol_Time(read_cgns_id, step)

        # start_time_outputからend_time_outputまで繰り返し出力
        if time >= start_time_output and time <= end_time_output:

            read_elevation_vale_bottom()
            triangle_configuration_node_list_bottom = make_tryangle(0)

            if output_stl == 1:
                make_polygon_stl(
                    bottom_elevation_vale_1d,
                    triangle_configuration_node_list_bottom,
                    "bottom",
                )

            if output_obj == 1:
                v_text = get_v(
                    coordinate_x_1d, coordinate_y_1d, bottom_elevation_vale_1d
                )
                vt_text = get_vt(coordinate_x_1d, coordinate_y_1d)
                f_text = get_f(triangle_configuration_node_list_bottom)
                make_polygon_obj(v_text, vt_text, f_text, "bottom")

            if add_water_surface == 1:
                read_elevation_vale_ws()
                triangle_configuration_node_list_ws = make_tryangle(0)

                if output_stl == 1:
                    make_polygon_stl(
                        ws_elevation_vale_1d, triangle_configuration_node_list_ws, "ws"
                    )

                if output_obj == 1:
                    v_text = get_v(
                        coordinate_x_1d, coordinate_y_1d, ws_elevation_vale_1d
                    )
                    vt_text = get_vt(coordinate_x_1d, coordinate_y_1d)
                    f_text = get_f(triangle_configuration_node_list_ws)
                    make_polygon_obj(v_text, vt_text, f_text, "ws")

    cgns_close()
