import iric
import sys
import numpy as np
from stl import mesh

# --------------------------------------------------
# メモ
# --------------------------------------------------
# CGNSから読み込む時は1次元配列、順番は以下
# --------------------------------------------------
#      j
#      ↑
#     4|  4,  9, 14, 19, 24, 29
#     3|  3,  8, 13, 18, 23, 28
#     2|  2,  7, 12, 17, 22, 27
#     1|  1,  6, 11, 16, 21, 26
#     0|  0,  5, 10, 15, 20, 25
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

    global n_step_read, elevation_name, save_location, n_cell
    global start_time_output, end_time_output
    global n_node_x, n_node_y, coordinate_x, coordinate_y
    global coordinate_x_1d, coordinate_y_1d, coordinate_x_2d, coordinate_y_2d

    # 読み込み用CGNSの計算ステップ数
    n_step_read = iric.cg_iRIC_Read_Sol_Count(read_cgns_id)
    # 読み込み用CGNSの標高のデータ名
    elevation_name = iric.cg_iRIC_Read_String(write_cgns_id, "elevation_name")
    # ファイルの保存場所
    save_location = iric.cg_iRIC_Read_String(write_cgns_id, "save_location")
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

    # CGNSから読み込んだcoordinate_x_1dとcoordinate_y_1dは1次元配列なので2次元配列にする
    coordinate_x_2d = np.array(coordinate_x_1d).reshape(n_node_x, n_node_y)
    coordinate_y_2d = np.array(coordinate_y_1d).reshape(n_node_x, n_node_y)


# --------------------------------------------------
# ポリゴンの頂点の座標(x,y,z)を3次元配列として作成する。
# --------------------------------------------------
def make_polygon_node_coordinate_list():

    global elevation_vale_1d, elevation_vale_2d, polygon_node_list

    elevation_vale = iric.cg_iRIC_Read_Sol_Node_Real(read_cgns_id, step, elevation_name)
    # CGNSから読み込んだelevation_valeをnumpy配列にする。
    elevation_vale_1d = np.array(elevation_vale)
    # CGNSから読み込んだelevation_valeは1次元配列なので2次元配列にする
    elevation_vale_2d = np.array(elevation_vale_1d).reshape(n_node_x, n_node_y)

    polygon_node_list = np.stack(
        [coordinate_x_1d, coordinate_y_1d, elevation_vale_1d], 1
    )


# --------------------------------------------------
# 三角形分割
# --------------------------------------------------
def make_tryangle():

    global triangle_configuration_node_list

    for i in range(n_node_x - 1):
        for j in range(n_node_y - 1):
            tryangle_tmp_1 = np.array(
                [i * n_node_y + j, (i + 1) * n_node_y + j, (i + 1) * n_node_y + j + 1],
                dtype=np.int64,
            )
            tryangle_tmp_2 = np.array(
                [i * n_node_y + j, i * n_node_y + j + 1, (i + 1) * n_node_y + j + 1],
                dtype=np.int64,
            )

            triangle_configuration_node_list[
                (i * (n_node_y - 1) + j) * 2
            ] = tryangle_tmp_1
            triangle_configuration_node_list[
                (i * (n_node_y - 1) + j) * 2 + 1
            ] = tryangle_tmp_2


def make_polygon_obj():

    global triangle_configuration_node_list
    global polygon_node_list

    polygon_obj = mesh.Mesh(
        np.zeros(triangle_configuration_node_list.shape[0], dtype=mesh.Mesh.dtype)
    )
    for i, f in enumerate(triangle_configuration_node_list):
        for j in range(3):
            polygon_obj.vectors[i][j] = polygon_node_list[f[j], :]

    polygon_obj.save(
        save_location + "\\" + "polygon_" + str("{:.2f}".format(time)) + ".stl"
    )


if __name__ == "__main__":

    ier = 0

    # if len(sys.argv) < 2:
    #     print("Error: CGNS file name not specified.")
    #     exit()

    # write_cgns_name = sys.argv[1]

    write_cgns_name = (
        "C:\WorkSpace\iRIC\iRICver4\project\stl_generator_test\stl_gen\Case1.cgn"
    )

    cgns_open()
    read_initial_condition()

    triangle_configuration_node_list = np.full((n_cell * 2, 3), 0)

    for step_tmp in range(n_step_read):

        # python は0からスタートなので1足しておく
        step = step_tmp + 1

        # 時間を読み込む
        time = iric.cg_iRIC_Read_Sol_Time(read_cgns_id, step)

        # start_time_outputからend_time_outputまで繰り返し出力
        if time >= start_time_output and time <= end_time_output:

            make_polygon_node_coordinate_list()
            make_tryangle()
            make_polygon_obj()

    cgns_close()
