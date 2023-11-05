# database info

Hopefully this info will be helpful in re-creating the database to support filtertube if needed. 


SQL to create the database

```
CREATE DATABASE `filtertube` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;
```

## tables

There are currently only two tables, as copying from req to req_history is what moves something from Pending to Approve/Deny. 
That's mostly so that only the req_history table is getting looped over by the downloader or future other jobs (auto-approver for white-listed channels perhaps?)



```
CREATE TABLE `req` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` varchar(512) DEFAULT NULL,
  `requestor` varchar(512) DEFAULT NULL,
  `video_name` varchar(512) DEFAULT NULL,
  `status` varchar(512) DEFAULT NULL,
  `URL` varchar(512) DEFAULT NULL,
  `channel_name` varchar(512) DEFAULT NULL,
  `video_title` varchar(512) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=150 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
```



```
CREATE TABLE `req_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` varchar(512) DEFAULT NULL,
  `requestor` varchar(512) DEFAULT NULL,
  `status` varchar(512) DEFAULT NULL,
  `video_name` varchar(512) DEFAULT NULL,
  `URL` varchar(512) DEFAULT NULL,
  `channel_name` varchar(512) DEFAULT NULL,
  `video_title` varchar(512) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=167 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
```