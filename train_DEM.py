from Mymodels.DEM import DEM
#import torch.optim as optim
#from torch.Utils.data import DataLoader
import matplotlib.pyplot as plt
#from SimpleClassfier.Claafier_Data_ready import ClassfierDataset
from Utils.prepare_data import *
from SimpleClassfier.Classfier import *
import time
from Data_ready import *

def adjust_learning_rate(optimizer, lr):
    """Sets the learning rate to the initial LR decayed by 10 every 30 epochs"""
    for param_group in optimizer.param_groups:
        param_group['lr'] = lr


def train_dem():
    model_path = 'models_file/DEM_attr.pt'
    batch_size = 32
    train_dataset = ClassfierDataset('../Data/data/train_data/')
    train_dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=1)
    semantic = word_embeding_get()
    semantic = torch.from_numpy(semantic).cuda()
    _, attribute = attribute_label()
    attribute = torch.from_numpy(attribute+0.00000001).cuda()
    myResnet = torch.load('./SimpleClassfier/classfier_model/classfier_unNorm_64.pt').res
    word_label = np.load('../Data/data/train_data/word_labels.npy')
    if os.path.exists(model_path):
        print('load modelfile')
        model = torch.load(model_path)
    else:

        model = DEM(myResnet)
    model.cuda()
    optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-4, weight_decay=1e-8)

    lr = 0.01
    epochs = 50
    loss_list = []
    min_loss = 999
    for i in range(epochs):
        count = 0.
        sum_loss = 0.
        start_time = time.time()
        model.train()

        for idx, batch_data in enumerate(train_dataloader):
            image = batch_data['image'].float().cuda()
            label = batch_data['label'].long().cuda()
            """
            if i%500 ==0 and i>0:
                lr = lr*0.991
                adjust_learning_rate(optimizer,lr)
            """
            model.zero_grad()
            loss = model.get_loss(image, label, semantic, attribute)
            loss.backward()
            optimizer.step()
            print('current loss: ' + str(loss.data) + ' batch/sum : ' + str(idx) + '/' + str(int(train_dataset.__len__() / batch_size)))
            count += 1
            sum_loss += float(loss)
        end_time = time.time()
        print("finish epoch " + str(i) + " with " + str(end_time - start_time) + "s")
        print("mean loos : " + str(sum_loss / count))
        loss_list.append(float(sum_loss / count))
        if sum_loss / count < min_loss:
            print("保存模型文件至: " + model_path)
            torch.save(model, model_path)
            print("loss declined:" + str(min_loss - sum_loss / count))
            min_loss = sum_loss / count
    plt.xlabel('Epochs')
    plt.ylabel('LOSS')
    plt.legend()
    plt.savefig("log_pics/DEM_loss.png")
    plt.clf()
    pass


def eval_DEM():
    word_labels, attributes = attribute_label()
    semantic = word_embeding_get()
    semantic = torch.from_numpy(semantic).cuda()
    eval_dataset = DEMPlusEvalDataset()
    eval_dataloader = DataLoader(eval_dataset, batch_size=1, shuffle=False, num_workers=1)
    model = torch.load('models_file/DEM_plus.pt')
    model.eval()

    sum_len = eval_dataset.__len__()
    got_it = 0
    for idx, batch_data in enumerate(eval_dataloader):
        image = batch_data['image'].float().cuda()
        label = batch_data['label']
        pre = model.predict(image, semantic)
        if word_labels[pre[0]] == label[0]:
            got_it += 1

        print('processed image ' + str(idx))
        print('pre: ' + word_labels[pre[0]] + ' ground_truth: ' + label[0] + ' got: ' + str(got_it))
    print(got_it / sum_len)


def get_result():
    # 训练文件目录，原文件结构无需改动
    test_path = '../Data/DatasetA_test_20180813/DatasetA_test/'
    result_file = open('result/submit_DEM.txt', 'a', encoding='utf-8')
    label_list = np.load('data/test_data/label_list.npy')
    images_name = np.load('data/test_data/images_name.npy')
    test_dataset = TestDataset()
    test_dataloader = DataLoader(test_dataset, batch_size=1, shuffle=False, num_workers=1)
    semantic = torch.from_numpy(test_dataset.semantic_features).float().cuda()
    model = torch.load('models_file/DEM.pt')
    model.eval()
    _, attribute = attribute_label()
    attribute = torch.from_numpy(attribute).cuda()
    for idx, batch_data in enumerate(test_dataloader):
        image = batch_data['image'].float().cuda()
        pre = model.predict(image, semantic, attribute)
        image_name = images_name[idx]
        ready_to_write_label = label_list[pre[0]]
        result_file.write(image_name + '\t' + ready_to_write_label + '\n')
        print('processed image ' + str(idx) + ': ' + image_name + '\t' + ready_to_write_label + '\n')
        # print(all_prediction)


if __name__ == "__main__":
    train_dem()
    pass
