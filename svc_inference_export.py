import os
import torch
import argparse
from omegaconf import OmegaConf

from model.generator import Generator


def load_model(checkpoint_path, model):
    assert os.path.isfile(checkpoint_path)
    checkpoint_dict = torch.load(checkpoint_path, map_location="cpu")
    saved_state_dict = checkpoint_dict["model_g"]
    if hasattr(model, "module"):
        state_dict = model.module.state_dict()
    else:
        state_dict = model.state_dict()
    new_state_dict = {}
    for k, v in state_dict.items():
        try:
            new_state_dict[k] = saved_state_dict[k]
        except:
            new_state_dict[k] = v
    if hasattr(model, "module"):
        model.module.load_state_dict(new_state_dict)
    else:
        model.load_state_dict(new_state_dict)
    return model


def save_model(model, checkpoint_path):
    if hasattr(model, 'module'):
        state_dict = model.module.state_dict()
    else:
        state_dict = model.state_dict()
    torch.save({'model_g': state_dict}, checkpoint_path)


def save_lora(model, checkpoint_path):
    if hasattr(model, 'module'):
        state_dict_adapter = model.module.adapter.state_dict()
        state_dict_conv_post = model.module.conv_post.state_dict()
        state_dict_activation_post = model.module.activation_post.state_dict()
    else:
        state_dict_adapter = model.adapter.state_dict()
        state_dict_conv_post = model.conv_post.state_dict()
        state_dict_activation_post = model.activation_post.state_dict()
    torch.save({
        'lora_adapter': state_dict_adapter,
        'lora_conv_post': state_dict_conv_post,
        'lora_activation_post': state_dict_activation_post,
    }, checkpoint_path)


def main(args):
    hp = OmegaConf.load(args.config)
    model = Generator(hp)
    load_model(args.checkpoint_path, model)
    save_model(model, "maxgan_g.pth")
    save_lora(model, "maxgan_lora.pth")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', type=str, required=True,
                        help="yaml file for config. will use hp_str from checkpoint if not given.")
    parser.add_argument('-p', '--checkpoint_path', type=str, required=True,
                        help="path of checkpoint pt file for evaluation")
    args = parser.parse_args()

    main(args)
