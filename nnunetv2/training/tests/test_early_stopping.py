import tempfile
from nnunetv2.training.nnUNetTrainer.nnUNetTrainer import nnUNetTrainer
from nnunetv2.training.logging.nnunet_logger import nnUNetLogger


def simulate_early_stopping():
    # Create a trainer-like object without running full __init__
    trainer = object.__new__(nnUNetTrainer)

    # Minimal attributes used by on_epoch_end
    trainer.local_rank = 1  # avoid rank 0 actions like plotting or saving
    trainer.output_folder = tempfile.mkdtemp(prefix='nnunet_test_')
    trainer.print_to_log_file = lambda *args, **kwargs: print(*args)

    # logger with required keys
    logger = nnUNetLogger()
    # initialize lists with one epoch of dummy values so indexing [-1] works
    for k in logger.my_fantastic_logging.keys():
        logger.my_fantastic_logging[k] = [0.0]
    trainer.logger = logger

    # early stopping parameters (match implementation defaults)
    trainer.early_stopping_monitor = 'ema_fg_dice'
    trainer.early_stopping_patience = 50
    trainer.early_stopping_min_epochs = 100
    trainer._early_stopping_counter = 0
    trainer._best_for_early_stopping = None
    trainer._should_early_stop = False

    # other attributes expected by on_epoch_end
    trainer._best_ema = None
    trainer.save_every = 50
    trainer.disable_checkpointing = True
    trainer.current_epoch = 0

    # Simulate a scenario: improve until epoch 40, then no improvement thereafter
    num_simulated_epochs = 200
    for epoch in range(num_simulated_epochs):
        # update logger lists to have values for this epoch
        # simulate train/val losses and dice per class
        trainer.logger.my_fantastic_logging['train_losses'].append(1.0)
        trainer.logger.my_fantastic_logging['val_losses'].append(1.0)
        trainer.logger.my_fantastic_logging['dice_per_class_or_region'].append([0.5])
        trainer.logger.my_fantastic_logging['epoch_start_timestamps'].append(epoch * 1.0)
        trainer.logger.my_fantastic_logging['epoch_end_timestamps'].append(epoch * 1.0 + 1.0)
        trainer.logger.my_fantastic_logging['lrs'].append(0.001)

        # ema_fg_dice improves until epoch 40, then plateaus
        if epoch <= 40:
            ema = 0.1 + 0.01 * epoch
        else:
            ema = 0.5  # plateau

        trainer.logger.my_fantastic_logging['ema_fg_dice'].append(ema)
        trainer.logger.my_fantastic_logging['mean_fg_dice'].append(ema)

        # call on_epoch_end to trigger early-stopping bookkeeping
        trainer.on_epoch_end()

        if trainer._should_early_stop:
            print(f"Early stopping triggered at epoch (1-indexed): {trainer.current_epoch}")
            return trainer.current_epoch

    print("Early stopping was not triggered in the simulated run")
    return None


if __name__ == '__main__':
    stop_epoch = simulate_early_stopping()
    print('Stop epoch:', stop_epoch)
