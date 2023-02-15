import iric
import sys
import numpy as np
import stl

write_cgns_name = None
read_cgns_name = None
write_cgns_id = None
read_cgns_id = None

elevation_name = None
elevation_vale = []
elevation_vale_1d = np.empty(0)
elevation_vale_2d = np.empty([0, 0])

n_step_read = None

start_time_output = None
end_time_output = None

n_node_x = None
n_node_y = None
n_cell = None

coordinate_x = []
coordinate_y = []
coordinate_x_1d = np.empty(0)
coordinate_y_1d = np.empty(0)
coordinate_x_2d = np.empty([0, 0])
coordinate_y_2d = np.empty([0, 0])

polygon_node_list = np.empty([0, 0, 0])
tryangle_list = np.empty([0, 0, 0])
tryangle_tmp_1 = np.empty(0)
tryangle_tmp_2 = np.empty(0)

#--------------------------------------------------
# 書き込みと読み込み用CGNSファイルを開く
#--------------------------------------------------
def cgns_open():
    write_cgns_id = iric.cg_iRIC_Open(write_cgns_name)

    read_cgns_name = iric.cg_iRIC_Read_String(write_cgns_id, "")
    read_cgns_id = iric.cg_iRIC_Open(read_cgns_id)

#--------------------------------------------------
# 書き込みと読み込み用CGNSファイルを閉じる
#--------------------------------------------------
def cgns_close():
    iric.cg_iRIC_Close(read_cgns_id)
    iric.cg_iRIC_Close(write_cgns_id)

#--------------------------------------------------
# 初期条件等を読み込む
#--------------------------------------------------
def read_initial_condition():
    # 読み込み用CGNSの計算ステップ数
    n_step_read = iric.cg_iRIC_Read_Sol_Count(read_cgns_id)
    # 読み込み用CGNSの標高のデータ名
    elevation_name = iric.cg_iRIC_Read_String(write_cgns_id, "elevation_name")
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
  

#--------------------------------------------------
# ポリゴンの頂点の座標(x,y,z)を3次元配列として作成する。
#--------------------------------------------------
def make_polygon_node_coordinate_list():

    elevation_vale = iric.cg_iRIC_Read_Sol_Node_Real(read_cgns_id, step)
    # CGNSから読み込んだcoordinate_xとcoordinate_yをnumpy配列にする。
    elevation_vale_1d = np.array(elevation_vale)
    # CGNSから読み込んだcoordinate_x_1dとcoordinate_y_1dは1次元配列なので2次元配列にする
    elevation_vale_2d = np.array(elevation_vale_1d).reshape(n_node_x, n_node_y)

    polygon_node_list = np.stack(coordinate_x_1d, coordinate_y_1d, elevation_vale_1d)

#--------------------------------------------------
# 三角形分割
#--------------------------------------------------
def make_tryangle():

    for i in range(n_node_x-1):
        for j in range(n_node_y-1):
            tryangle_tmp_1 = np.array([i*n_node_y + j, (i+1)*n_node_y + j, (i+1)*n_node_y + j+1])
            tryangle_tmp_2 = np.array([i*n_node_y + j, i*n_node_y + j+1, (i+1)*n_node_y + j+1])







if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Error: CGNS file name not specified.")
        exit()

    write_cgns_name = sys.argv[1]

    cgns_open()
    read_initial_condition()

    for step in range(n_step_read):
        
        # python は0からスタートなので1足しておく
        step += 1
        # 時間を読み込む
        time = iric.cg_iRIC_Read_Sol_Time(read_cgns_id, step)

        # start_time_outputからend_time_outputまで繰り返し出力
        if time >= start_time_output and time <= end_time_output:

            elevation_vale = iric.cg_iRIC_Read_Sol_Node_Real(read_cgns_id, step)








