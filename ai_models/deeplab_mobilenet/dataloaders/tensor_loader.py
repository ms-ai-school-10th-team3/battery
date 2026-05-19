from dataloaders.datasets import simple_tensor
from torch.utils.data import DataLoader


def make_tensor_data_loader(args, **kwargs):

    if args.dataset == 'simple':

        train_set = simple_tensor.SimpleTensorSegmentation(
            args,
            split='train'
        )

        val_set = simple_tensor.SimpleTensorSegmentation(
            args,
            split='val'
        )

        num_class = 4

        simple_tensor.SimpleTensorSegmentation.NUM_CLASSES = num_class

        train_loader = DataLoader(
            train_set,
            batch_size=args.batch_size,
            shuffle=True,
            **kwargs
        )

        val_loader = DataLoader(
            val_set,
            batch_size=args.batch_size,
            shuffle=False,
            **kwargs
        )

        test_loader = None

        return train_loader, val_loader, test_loader, num_class

    else:
        raise NotImplementedError(
            "Only simple tensor dataset is supported."
        )