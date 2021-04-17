
#%% 1. 라이브러리 및 데이터 불러오기 
import pandas as pd
import os 
from geopandas import GeoDataFrame
import pickle
from shapely.geometry import Point


cur_path = os.getcwd() # 경로 설정

subway_crd = pd.read_csv('지하철역_좌표.csv', encoding='cp949')
subway_line= pd.read_csv('서울교통공사 노선별 지하철역 정보.csv', encoding='cp949')



#%% 2. 지하철역 좌표에 노선 정보 추가하기 

line_ls = []
for i in range(len(subway_crd)): 
    cur_subway = subway_crd.iloc[i]['역이름']
    matched_line = subway_line.loc[subway_line['전철역명'] == cur_subway]
    
    if len(matched_line) > 0 : 
        line_ls.append(list(matched_line['호선']))
        
    else: 
        line_ls.append(None)

subway_crd['호선'] = line_ls # 호선 정보 부여
subway_crd.dropna(subset=['호선'], inplace=True, axis=0) # 수도권 지하철역 좌표는 노선 정보가 안들어갔으므로 제거 

subway_crd['geometry'] = subway_crd.apply(lambda x: Point(x['x'], x['y']), axis=1) # 좌표 정보를 합쳐서 geometry 정보 부여  
subway_crd_gdf = GeoDataFrame(subway_crd, crs='EPSG:4326', geometry='geometry') # 좌표계 지정



#%% 3. 저장 + 불러오기 함수 설정  
def write_data(data, name):
    with open(name + '.bin', 'wb') as f:
        pickle.dump(data, f)
        
        
def load_data(name):
    with open(name + '.bin', 'rb') as f:
        data = pickle.load(f)
    return data  


#%% 4. 데이터 저장 

# bin 데이터 -- 파이썬 활용 용도 (ArcGIS/QGIS 시각화 용도 x)
write_data(subway_crd_gdf, 'subway_crd_4326')
subway_crd_5179 = subway_crd_gdf.to_crs(epsg=5179) # 거리 계산을 위한 좌표계로 변환 후 저장
write_data(subway_crd_5179, 'subway_crd_5179')


# 나중에 bin 데이터 다시 불러올 때 
subway_crd_4326 = load_data('subway_crd_4326')
subway_crd_5179 = load_data('subway_crd_5179')



# 노선 정보를 빼고 좌표 데이터 
subway_crd_5179 = subway_crd_5179.drop(['호선'], axis=1)
subway_crd_5179.to_file('subway_crd_5179.geojson', driver='GeoJSON')



