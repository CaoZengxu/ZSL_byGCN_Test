from Data_ready import TestDataset
from torch.utils.data import DataLoader
from Utils import *
import torch
import numpy as np
# 训练文件目录，原文件结构无需改动
test_path = '../Data/DatasetA_test_20180813/DatasetA_test/'
result_file = open('result/submit_spared.txt', 'a', encoding='utf-8')
label_list = np.load('test_data/label_list.npy')
images_name = np.load('test_data/images_name.npy')
if __name__=='__main__':

    test_dataset = TestDataset()
    test_dataloader = DataLoader(test_dataset, batch_size=1, shuffle=False, num_workers=1)
    semantic = torch.from_numpy(test_dataset.semantic_features).float().cuda()

    model = torch.load('gcn_zsl.pt')
    model.eval()
    myResnet = torch.load('./SimpleClassfier/classfier_model/classfier.pt').res
    myResnet.cuda()
    myResnet.eval()
    for idx, batch_data in enumerate(test_dataloader):
        image = batch_data['image'].float().cuda()
        test_image = image
        test_image_feature = myResnet(test_image)
        semantic_feature = model(semantic)
        all_prediction = torch.mm(test_image_feature, torch.t(semantic_feature)).cpu().detach().numpy()
        loc = np.where(all_prediction == np.max(all_prediction))
        loc = loc[1][-1]
        image_name = images_name[idx]
        ready_to_write_label = label_list[loc]
        result_file.write(image_name+'\t'+ready_to_write_label+'\n')
        print('processed image '+str(idx)+': '+image_name+'\t'+label_list[loc]+'\n')
        #print(all_prediction)
    pass




