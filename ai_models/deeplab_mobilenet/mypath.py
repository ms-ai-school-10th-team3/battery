class Path(object):
    @staticmethod
    def db_root_dir(dataset):
        if dataset == 'pascal':
            return '/path/to/datasets/VOCdevkit/VOC2012/'

        elif dataset == 'sbd':
            return '/path/to/datasets/benchmark_RELEASE/'

        elif dataset == 'cityscapes':
            return '/path/to/datasets/cityscapes/'

        elif dataset == 'coco':
            return '/path/to/datasets/coco/'

        elif dataset == 'simple':
            return r'D:\1차 팀프로젝트\모델_배터리 불량 이미지 데이터\1.모델.zip\1.모델소스코드\모델1_DeepLabv3\pytorch-deeplab-xception-eval\battery_sample_512'

        else:
            print('Dataset {} not available.'.format(dataset))
            raise NotImplementedError