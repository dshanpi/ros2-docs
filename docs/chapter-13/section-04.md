---
title: "13.4 Linux SPI设备驱动"
sidebar_label: "13.4 Linux SPI设备驱动"
slug: /chapter-13/section-04/
---

dac\_drv.c源码如下所示：

```c
/* 定义IOCTL命令 */
#define SPI_IOC_WR _IOW('k', 1, int)

/* 设备私有数据结构 */
struct dac_device {
    struct spi_device *spi;
    struct device *chr_dev;
    struct cdev cdev;
    dev_t devt;
};

static struct class *spidev_class;
static int major;
static struct dac_device *dac_dev;

/* SPI传输函数 */
static long spidev_ioctl(struct file *filp, unsigned int cmd, unsigned long arg)
{
    int val, status;  // 修复：移除未使用的err变量
    unsigned char tx_buf[2];
    unsigned char rx_buf[2];
    struct spi_message msg;
    struct spi_transfer xfer[1];
    struct dac_device *dev = filp->private_data;
    
    memset(&xfer[0], 0, sizeof(xfer));
    
    /* 从用户空间复制数据 */
    if (copy_from_user(&val, (const void __user *)arg, sizeof(int))) {
        return -EFAULT;
    }
    
    printk("spidev_ioctl get val from user: %d\n", val);
    
    /* 1. 将val转换为DAC要求的格式 */
    val <<= 2;     /* bit0,bit1 = 0b00 */
    val &= 0xFFC;  /* 只保留10bit */
    
    tx_buf[1] = val & 0xff;
    tx_buf[0] = (val >> 8) & 0xff;
    
    /* 2. 发起SPI传输 */
    xfer[0].tx_buf = tx_buf;
    xfer[0].rx_buf = rx_buf;
    xfer[0].len = 2;
    
    spi_message_init(&msg);
    spi_message_add_tail(&xfer[0], &msg);
    
    status = spi_sync(dev->spi, &msg);
    if (status < 0) {
        printk("SPI transfer error: %d\n", status);
        return status;
    }
    
    /* 3. 修改读回数据的格式 */
    val = (rx_buf[0] << 8) | (rx_buf[1]);
    val >>= 2;
    
    /* 将结果复制回用户空间 */
    if (copy_to_user((void __user *)arg, &val, sizeof(int))) {
        return -EFAULT;
    }
    
    return 0;
}

/* 文件操作函数 */
static int spidev_open(struct inode *inode, struct file *filp)
{
    struct dac_device *dev = container_of(inode->i_cdev, struct dac_device, cdev);
    filp->private_data = dev;
    return 0;
}

static int spidev_release(struct inode *inode, struct file *filp)
{
    return 0;
}

/* 文件操作结构体 */
static const struct file_operations spidev_fops = {
    .owner = THIS_MODULE,
    .unlocked_ioctl = spidev_ioctl,
    .open = spidev_open,
    .release = spidev_release,
};

/* 设备树匹配表 */
static const struct of_device_id spidev_dt_ids[] = {
    { .compatible = "100ask,dac" },
    {},
};
MODULE_DEVICE_TABLE(of, spidev_dt_ids);

/* 探测函数 */
static int spidev_probe(struct spi_device *spi)
{
    struct dac_device *dev;
    int ret;
    
    /* 分配设备私有数据 */
    dev = devm_kzalloc(&spi->dev, sizeof(*dev), GFP_KERNEL);
    if (!dev)
        return -ENOMEM;
    
    dev->spi = spi;
    spi_set_drvdata(spi, dev);
    
    /* 配置SPI参数 */
    spi->mode = SPI_MODE_0;  // 根据DAC要求设置模式
    spi->bits_per_word = 8;  // 8位数据
    ret = spi_setup(spi);
    if (ret < 0) {
        dev_err(&spi->dev, "SPI setup failed: %d\n", ret);
        return ret;
    }
    
    /* 动态分配字符设备号 */
    ret = alloc_chrdev_region(&dev->devt, 0, 1, "100ask_dac");
    if (ret < 0) {
        dev_err(&spi->dev, "Failed to allocate char device region\n");
        return ret;
    }
    major = MAJOR(dev->devt);
    
    /* 初始化cdev结构 */
    cdev_init(&dev->cdev, &spidev_fops);
    dev->cdev.owner = THIS_MODULE;
    
    /* 添加cdev到系统 */
    ret = cdev_add(&dev->cdev, dev->devt, 1);
    if (ret < 0) {
        dev_err(&spi->dev, "Failed to add char device\n");
        unregister_chrdev_region(dev->devt, 1);
        return ret;
    }
    
    /* 创建设备类 - 使用单参数版本 */
    spidev_class = class_create("100ask_dac");  
    if (IS_ERR(spidev_class)) {
        ret = PTR_ERR(spidev_class);
        cdev_del(&dev->cdev);
        unregister_chrdev_region(dev->devt, 1);
        return ret;
    }
    
    /* 创建设备节点 */
    dev->chr_dev = device_create(spidev_class, &spi->dev, dev->devt, NULL, "100ask_dac");
    if (IS_ERR(dev->chr_dev)) {
        ret = PTR_ERR(dev->chr_dev);
        class_destroy(spidev_class);
        cdev_del(&dev->cdev);
        unregister_chrdev_region(dev->devt, 1);
        return ret;
    }
    
    dac_dev = dev;
    dev_info(&spi->dev, "SPI DAC driver probed successfully\n");
    return 0;
}

/* 移除函数 - 返回void类型 */
static void spidev_remove(struct spi_device *spi)  
{
    struct dac_device *dev = spi_get_drvdata(spi);
    
    /* 销毁设备节点 */
    device_destroy(spidev_class, dev->devt);
    
    /* 删除cdev */
    cdev_del(&dev->cdev);
    
    /* 释放设备号 */
    unregister_chrdev_region(dev->devt, 1);
    
    dev_info(&spi->dev, "SPI DAC driver removed\n");
    // 注意：不再需要return语句
}

/* SPI驱动结构体 */
static struct spi_driver spidev_spi_driver = {
    .driver = {
        .name = "100ask_spi_dac_drv",
        .of_match_table = of_match_ptr(spidev_dt_ids),
    },
    .probe = spidev_probe,
    .remove = spidev_remove,  // 匹配void返回类型
};

```
