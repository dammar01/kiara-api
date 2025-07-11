import torch


class CommonHelper:
    def check_cuda(self):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print("Using device:", device)
        print()
        if device.type == "cuda":
            print(torch.cuda.get_device_name(0))
            print("Memory Usage:")
            print(
                "Allocated:", round(torch.cuda.memory_allocated(0) / 1024**3, 1), "GB"
            )
            print("Cached:   ", round(torch.cuda.memory_reserved(0) / 1024**3, 1), "GB")
