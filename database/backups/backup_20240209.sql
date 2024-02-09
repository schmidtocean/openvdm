-- MySQL dump 10.13  Distrib 8.0.36, for Linux (x86_64)
--
-- Host: localhost    Database: openvdm
-- ------------------------------------------------------
-- Server version	8.0.36-0ubuntu0.22.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `OVDM_CollectionSystemTransfers`
--

DROP TABLE IF EXISTS `OVDM_CollectionSystemTransfers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `OVDM_CollectionSystemTransfers` (
  `collectionSystemTransferID` int unsigned NOT NULL AUTO_INCREMENT,
  `name` tinytext NOT NULL,
  `longName` text,
  `cruiseOrLowering` int unsigned NOT NULL DEFAULT '0',
  `sourceDir` tinytext,
  `destDir` tinytext,
  `staleness` int DEFAULT '0',
  `useStartDate` tinyint(1) DEFAULT '0',
  `transferType` int unsigned NOT NULL,
  `localDirIsMountPoint` int unsigned NOT NULL DEFAULT '0',
  `rsyncServer` tinytext,
  `rsyncUser` tinytext,
  `rsyncPass` tinytext,
  `smbServer` tinytext,
  `smbUser` tinytext,
  `smbPass` tinytext,
  `smbDomain` tinytext,
  `sshServer` tinytext,
  `sshUser` tinytext,
  `sshUseKey` int unsigned NOT NULL DEFAULT '0',
  `sshPass` tinytext,
  `includeFilter` text,
  `excludeFilter` text,
  `ignoreFilter` text,
  `status` int unsigned NOT NULL DEFAULT '3',
  `enable` tinyint(1) NOT NULL DEFAULT '0',
  `pid` int unsigned DEFAULT '0',
  `bandwidthLimit` int unsigned NOT NULL DEFAULT '0',
  `skipEmptyDirs` int unsigned NOT NULL DEFAULT '1',
  `skipEmptyFiles` int unsigned NOT NULL DEFAULT '1',
  `syncFromSource` int unsigned NOT NULL DEFAULT '0',
  `removeSourceFiles` int unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`collectionSystemTransferID`),
  KEY `CollectionSystemTransferStatus` (`status`),
  KEY `CollectionSystemTransferType` (`transferType`),
  CONSTRAINT `CollectionSystemTransferStatus` FOREIGN KEY (`status`) REFERENCES `OVDM_Status` (`statusID`),
  CONSTRAINT `CollectionSystemTransferType` FOREIGN KEY (`transferType`) REFERENCES `OVDM_TransferTypes` (`transferTypeID`)
) ENGINE=InnoDB AUTO_INCREMENT=63 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `OVDM_CollectionSystemTransfers`
--

LOCK TABLES `OVDM_CollectionSystemTransfers` WRITE;
/*!40000 ALTER TABLE `OVDM_CollectionSystemTransfers` DISABLE KEYS */;
INSERT INTO `OVDM_CollectionSystemTransfers` VALUES (1,'UHDAS_1','UHDAS 1 (Primary)',0,'/home/data','Falkor_too/Raw/ADCP/',5,0,4,0,'','','','','','','','10.23.10.73','adcp',0,'soi_uh14.','*{cruiseID}*/*','','*00mount_test*,*archive_dailyreports/*',2,1,0,0,1,1,0,0),(2,'SBE_CTD','SBE 911+ CTD',0,'CTD/Raw/{cruiseID}','Falkor_too/Raw/CTD',5,0,3,0,'','','','//10.23.10.75/D','Operator','simrad0','WORKGROUP','','',0,'','*,*.hex,*.asvp','','',2,1,0,0,1,1,0,0),(5,'EK80','EK80 Split-beam Echo Sounder',0,'EK80/{cruiseID}','Falkor_too/Raw/EK80',5,0,3,0,'','','','//10.23.10.66/D','Operator','simrad0','WORKGROUP','','',0,'','*','','',4,0,0,0,1,1,0,0),(6,'EM124','EM124 Multibeam Mapping System',0,'sisdata/raw/{cruiseID}_4','Falkor_too/Raw/EM124/',5,0,3,0,'','','','//10.23.10.60/D$','Operator','simrad0','WORKGROUP','','',0,'','*_{cruiseID}_EM124*.*','*kmwcd_frag','*9999.kmall,*.asvp*,*.temp*,*.abs*,*kmwcd_frag',2,1,0,0,1,1,0,0),(8,'EM124_Bist','EM124 Bist Results',0,'sisdata/common/BIST/{cruiseID}','Falkor_too/Raw/EM124/Bist_Results',0,0,3,0,'','','','//10.23.10.60/D$','Operator','simrad0','WORKGROUP','','',0,'','*','','',2,1,0,0,1,1,0,0),(9,'EM712','EM712 Multibeam Mapping System',0,'sisdata/raw/{cruiseID}','Falkor_too/Raw/EM712',5,0,3,0,'','','','//10.23.10.62/d','Operator','simrad0','WORKGROUP','','',0,'','*','','*.asvp,*.temp,*.abs,*9999.kmall,*kmwcd_frag',2,1,0,0,1,1,0,0),(11,'EM712_BIST','EM712 Bist Results',0,'sisdata/common/BIST/{cruiseID}','Falkor_too/Raw/EM712/Bist_Results',5,0,3,0,'','','','//10.23.10.62/D','Operator','simrad0','WORKGROUP','','',0,'','*','','',2,1,0,0,1,1,0,0),(12,'Exported_SSP_from_SSM','SSP Files Exported from SSM for post processing',0,'SSM_SVP/{cruiseID}','Falkor_too/Processed/Preliminary/Sound_Speed_Files/',5,1,3,0,'','','','//10.23.10.75/D','Operator','simrad0','WORKGROUP','','',0,'','*/{cruiseID}_CTD_[0-9][0-9][0-9]*,*/{cruiseID}_{loweringID}_SVP_ROV_DOWNCAST.bsvp,*/{cruiseID}_{loweringID}_SVP_ROV_DOWNCAST.asvp,*','','',3,0,0,0,1,1,0,0),(14,'SBP29','SBP29 Sub-Bottom Profiler',0,'SBP29/{cruiseID}','Falkor_too/Raw/SBP29',5,0,3,0,'','','','//10.23.10.69/e$','Operator','simrad0','WORKGROUP','','',0,'','*','','',1,1,1537,0,1,1,0,0),(15,'Magnetometer','Raw Magnetometer From BOB',0,'MAGNETOMETER','Falkor_too/Raw/Magnetometer',0,1,3,0,'','','','//10.23.10.75/D_PH_DATA','Operator','simrad0','WORKGROUP','','',0,'','*','','',3,0,0,0,1,1,0,0),(16,'ParticipantData','From ParticipantData Share',0,'/mnt/soi_data1/vault/ParticipantData','ParticipantData',5,1,1,0,'','','','','','','','','',0,'','*','*.exe,*.bat,*.pkg,*.img','*/.DS_Store,*/Thumbs.db',3,0,0,0,1,1,0,0),(17,'pH','pH Sensor',0,'{cruiseID}/AFT_pH_2_AP0013','Falkor_too/Raw/pH',5,1,3,0,'','','','//10.23.10.52/pH','localuser','admin4@llMT','WORKGROUP','','',0,'','*','','',2,1,0,0,1,1,0,0),(18,'POSMV_PPP','POSMV PPP Raw Data Logging',0,'{cruiseID}','Falkor_too/Raw/POSMV',5,0,3,0,'','','','//10.23.10.52/POSMV_PPP_RAW','localuser','admin4@llMT','WORKGROUP','','',0,'','*/{cruiseID}_POSMV_RAW.*,*/{cruiseID}_POSMV_RAW_2.*','','',2,1,0,0,1,1,0,0),(19,'Processed_MB','Processed Multibeam Data',0,'{cruiseID}','Falkor_too/Processed/Final/Final_MB_Products',0,0,3,0,'','','','//10.23.9.62/final-data-for-CruiseData-sync','operator','Simrad2022','ad.falkortoo.org','','',0,'','*','','',3,0,0,0,1,1,0,0),(20,'ScienceData','From ScienceData Share',0,'/mnt/soi_data1/vault/ScienceData','Science',0,0,1,0,'','','','','','','','','',0,'','*','*.exe,*.bat,*.pkg,*.img','*/.DS_Store,*/Thumbs.db',4,0,0,0,1,1,0,0),(21,'OpenRVDAS','OpenRVDAS',0,'/data/openrvdas','Falkor_too/Raw/OpenRVDAS',0,1,4,0,'','','','','','','','10.23.9.21','mt',0,'Dragon2017','*{cruiseID}_*.txt,*{cruiseID}_*.bin','','',2,1,0,0,1,1,0,0),(22,'SVX2','SVX2',0,'CTD_SVX2/{cruiseID}','Falkor_too/Raw/SVP',5,1,3,0,'','','','//10.23.10.75/D','Operator','simrad0','WORKGROUP','','',0,'','*/{cruiseID}_[0-9][0-9][0-9].pro,*/{cruiseID}_{loweringID}_SVP_ROV_DOWNCAST.pro,*/{cruiseID}_[0-9][0-9][0-9]*kHz.abs,*/{cruiseID}_{loweringID}_SVP_ROV_DOWNCAST*kHz.abs','','*.bsvp,*.asvp',3,0,0,0,1,1,0,0),(24,'XBT','Turo XBT',0,'XBT/{cruiseID}','Falkor_too/Raw/XBT',5,1,3,0,'','','','//10.23.10.75/D','Operator','simrad0','WORKGROUP','','',0,'','*{cruiseID}.db,*{cruiseID}_[0-9][0-9][0-9].nc,*{cruiseID}_[0-9][0-9][0-9].csv,*{cruiseID}_[0-9][0-9][0-9].jjv,*{cruiseID}_[0-9][0-9][0-9].svp,*{cruiseID}/dropStatus.csv,*export/{cruiseID}.kml,*','pseudofileXXXXXX','',2,1,0,0,0,0,1,0),(25,'S5K_SCICAM_DVR','ROV SCI Camera - DVR Recording',1,'/home/soi/videos','Video/SCICAM',5,1,4,0,'','','','','','','','10.23.46.60','soi',0,'SOI4awesome','*.mov','','',2,1,0,0,1,1,0,1),(29,'UHDAS_2','UHDAS 2 (Backup)',0,'/home/data','Falkor_too/Raw/ADCP_BKUP/',0,0,4,0,'','','','','','','','10.23.10.74','adcp',0,'soi_uh14.','*{cruiseID}*/*','','*00mount_test*,*archive_dailyreports/*,*0uhdas/*',2,1,0,0,0,0,0,0),(30,'EA440','EA440 Single-beam Echo Sounder',0,'EA440/{cruiseID}','Falkor_too/Raw/EA440',20,1,3,0,'','','','//10.23.10.67/G$','Operator','simrad0','WORKGROUP','','',0,'','*.raw,*.idx','','',4,0,0,0,0,0,0,0),(31,'EA640','EA640 Single-beam Echo Sounder',0,'EA640/{cruiseID}','Falkor_too/Raw/EA640',0,0,3,0,'','','','//10.23.10.68/G$','Operator','simrad0','WORKGROUP','','',0,'','*L[0-9][0-9][0-9][0-9]-{cruiseID}-D[2-3][0-9][0-1][0-9][0-3][0-9]-T[0-2][0-3][0-5][0-9][0-9][0-9].raw,*L[0-9][0-9][0-9][0-9]-{cruiseID}-D[2-3][0-9][0-1][0-9][0-3][0-9]-T[0-2][0-3][0-5][0-9][0-9][0-9].idx','','',3,0,0,0,0,0,0,0),(32,'EM2040','EM2040 Multibeam Mapping System',0,'sisdata/raw/{cruiseID}','Falkor_too/Raw/EM2040',5,1,3,0,'','','','//10.23.10.64/E$','Operator','simrad0','WORKGROUP','','',0,'','*_{cruiseID}_EM2040.*','','*9999.kmall,*.asvp*,*.temp*,*.abs*,*kmwcd_frag',2,1,0,0,1,1,1,0),(33,'EM2040_Bist','EM2040 Bist Results',0,'sisdata/common/BIST/{cruiseID}','Falkor_too/Raw/EM2040/Bist_Results',0,0,3,0,'','','','//10.23.10.64/E$','Operator','simrad0','WORKGROUP','','',0,'','*','','',2,1,0,0,1,1,0,0),(35,'S5K_SITCAM_DVR','ROV SIT Camera - DVR Recording',1,'/home/soi/videos/','Video/SITCAM',5,1,4,0,'','','','','','','','10.23.46.61','soi',1,NULL,'*.mov','','',2,1,0,0,1,1,0,1),(36,'S5K_HDQUAD_DVR','ROV HD Quad - DVR Recording',1,'/home/soi/videos','Video/HDQUAD',5,1,4,0,'','','','','','','','10.23.46.62','soi',1,NULL,'*.mov','','',4,0,0,0,1,1,0,1),(37,'S5K_SDQUAD_DVR','ROV SD Quad - DVR Recording',1,'/home/soi/videos','Video/SDQUAD',5,1,4,0,'','','','','','','','10.23.46.63','soi',1,NULL,'*.mov','','',4,0,0,0,1,1,0,1),(38,'S5K_SCITOO_DVR','ROV SCITOO Camera - DVR Recording',1,'/home/soi/videos','Video/SCITOO',5,1,4,0,'','','','','','','','10.23.46.64','soi',1,NULL,'*.mov','','',4,0,0,0,1,1,0,1),(39,'S5K_SITTOO_DVR','ROV SITTOO Camera - DVR Recording',1,'/home/soi/videos','Video/SITTOO',5,1,4,0,'','','','','','','','10.23.46.65','soi',1,NULL,'*.mov','','',4,0,0,0,1,1,0,1),(40,'PI_NAS_PARTICIPANT','Participant data from the PI_NAS',0,'/net/PI-NAS/{cruiseID}/ParticipantData','ParticipantData',5,1,1,0,'','','','','','','','','',0,'','*','*.exe,*.bat,*.pkg,*.img,*@eaDir*','*/.DS_Store,*/Thumbs.db,.rsync,lost+found,lost?found,.Spotlight-V100,.fseventsd,.Trash,1000,.Trashes,._.Trashes,.TemporaryItems,._.TemporaryItems,.DS_Store,Thumbs.db,ld.so.cache,.Recycle_Bin,$RECYCLE.BIN,.@__thumb,*.pvm,Backups.backupdb,@eaDir',4,0,0,0,1,1,1,0),(41,'EM124_SRH','EM124 Seapath Roll Heave',0,'sisdata/common/srh','Falkor_too/Raw/EM124/SRH/',0,1,3,0,'','','','//10.23.10.60/D$','Operator','simrad0','WORKGROUP','','',0,'','*','','',2,1,0,0,1,1,0,0),(42,'EM712_SRH','EM712 Seapath Roll Heave',0,'sisdata/common/srh','Falkor_too/Raw/EM712/SRH/',0,1,3,0,'','','','//10.23.10.62/D','Operator','simrad0','WORKGROUP','','',0,'','*','','',2,1,0,0,1,1,0,0),(43,'EM2040_SRH','EM2040 Seapath Roll Heave',0,'sisdata/common/srh','Falkor_too/Raw/EM2040/SRH/',0,1,3,0,'','','','//10.23.10.64/E$','Operator','simrad0','WORKGROUP','','',0,'','*','','',2,1,0,0,1,1,0,0),(44,'SCI-NAV-Multibeam','SCI-NAV Multibeam Mapping M3',1,'{cruiseID}/M3','M3',5,1,3,0,'','','','//10.23.9.70/f','localuser','admin4@llMT','WORKGROUP','','',0,'','*','','',4,0,0,0,1,1,0,0),(45,'Working_MB','Working Multibeam Data',0,'{cruiseID}','Falkor_too/Processed/Preliminary/Processed_MB',5,0,3,0,'','','','//10.23.9.62/multibeam-working-data-sync','operator','Simrad2022','ad.falkortoo.org','','',0,'','*','','',4,0,0,0,1,1,0,0),(46,'ROV_Sprint_Raw','ROV Sprint Raw',1,'Hub/Logfiles','Sprint',5,1,3,0,'','','','//10.23.48.20/Sonardyne','openvdm','Dragon2017','WORKGROUP','','',0,'','*.bin','','',4,0,0,0,0,0,0,0),(47,'SCI-NAV-ADCP','SCI-NAV Syrinx ADCP',1,'{cruiseID}/Syrinx','Syrinx',5,1,3,0,'','','','//10.23.9.70/f','localuser','admin4@llMT','WORKGROUP','','',0,'','*.pd0','','',3,0,0,0,1,1,0,1),(48,'gdrive_cal_docs','Google Drive Calibration Documents',0,'/mnt/gdrive_cal_docs','Docs/Falkor_too',0,0,1,1,'','','','','','','','','',0,'','*','*ARCHIVED*,*/.DS_Store,*/Thumbs.db','',2,1,0,0,0,0,0,0),(51,'Processed_CTD','Processed CTD Data',0,'CTD/Processed/{cruiseID}','Falkor_too/Processed/Preliminary/Processed_CTD',0,0,3,0,'','','','//10.23.10.75/D','Operator','simrad0','WORKGROUP','','',0,'','*','','',2,1,0,0,1,1,0,0),(52,'PSONNAV_4DNav','PSONNAV data from 4DNav',1,'4DNav_Projects/Falkortoo_Setup/Local/Station/Data/RawData/ROV_Sprint_POSONAV/','Sprint/PSONNAV',0,1,3,0,'','','','//10.23.10.22/D$','localuser','admin4@llMT','WORKGROUP','','',0,'','*','','',3,0,0,0,0,0,0,0),(54,'SBP29-Processed','SBP29 Sub-Bottom Profiler Processed SEG-Y',0,'{cruiseID}','Falkor_too/Processed/Preliminary/Processed_SBP29',5,0,3,0,'','','','//10.23.10.69/f$','Operator','simrad0','WORKGROUP','','',0,'','*','','',1,1,1045655,0,1,1,0,0),(58,'Working-M3','M3-Multibeam-Processing-Projects',0,'/net/PI-NAS/{cruiseID}/ParticipantData/Mapping/M3/FKt231024_M3_Qimera_Projects','Falkor_too/Processed/Preliminary/Processed_M3',5,0,1,0,'','','','','','','','','',0,'','*','','',4,0,0,0,0,1,0,0),(59,'M3-Final','M3-Multibeam-Final-Products',0,'/net/PI-NAS/{cruiseID}/ParticipantData/Mapping/M3/FKt231024_M3_Final_Products','Falkor_too/Processed/Final/Final_MB_Products/Final_M3',5,0,1,0,'','','','','','','','','',0,'','*','','',3,0,0,0,0,1,0,0),(60,'Exported_SSP_from_SSM','SSP Files Exported from SSM for post processing Temporary',0,'SSM_SVP/{cruiseID}','Falkor_too/Processed/Preliminary/Sound_Speed_Files/',5,1,3,0,'','','','//10.23.9.104/d$','localuser','admin4@llMT','WORKGROUP','','',0,'','*/{cruiseID}_CTD_[0-9][0-9][0-9]*,*/{cruiseID}_{loweringID}_SVP_ROV_DOWNCAST.bsvp,*/{cruiseID}_{loweringID}_SVP_ROV_DOWNCAST.asvp,*','','',2,1,0,0,1,1,0,0),(61,'Exported_SSP_from_SSM','SSP Files Exported from SSM for post processing (VM)',0,'{cruiseID}','Falkor_too/Processed/Preliminary/Sound_Speed_Files/',5,1,3,0,'','','','//10.23.9.27/SSM_SVP','operator','simrad0','WORKGROUP','','',0,'','*/{cruiseID}_CTD_[0-9][0-9][0-9]*,*/{cruiseID}_{loweringID}_SVP_ROV_DOWNCAST.bsvp,*/{cruiseID}_{loweringID}_SVP_ROV_DOWNCAST.asvp,*','','',2,1,0,0,1,1,0,0),(62,'SAMOS','SAMOS Export Via Display VM',0,'/data/samos/','Falkor_too/Processed/SAMOS/',5,1,4,0,'','','','','','','','10.23.9.24','mt',0,'Dragon2017','*.csv','','',2,1,0,0,1,1,0,0);
/*!40000 ALTER TABLE `OVDM_CollectionSystemTransfers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `OVDM_CoreVars`
--

DROP TABLE IF EXISTS `OVDM_CoreVars`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `OVDM_CoreVars` (
  `coreVarID` int unsigned NOT NULL AUTO_INCREMENT,
  `name` tinytext NOT NULL,
  `value` tinytext,
  PRIMARY KEY (`coreVarID`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `OVDM_CoreVars`
--

LOCK TABLES `OVDM_CoreVars` WRITE;
/*!40000 ALTER TABLE `OVDM_CoreVars` DISABLE KEYS */;
INSERT INTO `OVDM_CoreVars` VALUES (1,'shipboardDataWarehouseIP','10.23.9.20'),(2,'shipboardDataWarehouseUsername','mt'),(4,'shipboardDataWarehouseStatus','2'),(5,'cruiseID','FKt240108'),(6,'cruiseStartDate','2024/01/08 00:00'),(7,'cruiseEndDate','2024/02/11 23:45'),(8,'cruiseSize','11614164762726'),(9,'cruiseSizeUpdated','2024/02/01 06:38:55'),(10,'loweringID','FKt240108_S0651'),(11,'loweringStartDate','2024/02/09 10:00'),(12,'loweringEndDate',''),(13,'loweringSize','35102'),(14,'loweringSizeUpdated','2024/02/09 03:32:52'),(15,'systemStatus','On'),(16,'shipToShoreBWLimitStatus','Off'),(17,'md5FilesizeLimit','10'),(18,'md5FilesizeLimitStatus','On'),(19,'showLoweringComponents','Yes'),(20,'cruiseStartPort','Valparaiso, Chile'),(21,'cruiseEndPort','Valparaiso, Chile');
/*!40000 ALTER TABLE `OVDM_CoreVars` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `OVDM_CruiseDataTransfers`
--

DROP TABLE IF EXISTS `OVDM_CruiseDataTransfers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `OVDM_CruiseDataTransfers` (
  `cruiseDataTransferID` int unsigned NOT NULL AUTO_INCREMENT,
  `name` tinytext NOT NULL,
  `longName` text,
  `transferType` int unsigned NOT NULL,
  `destDir` tinytext,
  `localDirIsMountPoint` int unsigned NOT NULL DEFAULT '0',
  `rsyncServer` tinytext,
  `rsyncUser` tinytext,
  `rsyncPass` tinytext,
  `smbServer` tinytext,
  `smbUser` tinytext,
  `smbPass` tinytext,
  `smbDomain` tinytext,
  `sshServer` tinytext,
  `sshUser` tinytext,
  `sshUseKey` int unsigned NOT NULL DEFAULT '0',
  `sshPass` tinytext,
  `status` int unsigned NOT NULL DEFAULT '3',
  `enable` tinyint(1) NOT NULL DEFAULT '0',
  `required` tinyint(1) NOT NULL DEFAULT '0',
  `pid` int unsigned DEFAULT '0',
  `bandwidthLimit` int unsigned NOT NULL DEFAULT '0',
  `includeOVDMFiles` int unsigned NOT NULL DEFAULT '0',
  `includePublicDataFiles` int unsigned NOT NULL DEFAULT '0',
  `excludedCollectionSystems` tinytext,
  `excludedExtraDirectories` tinytext,
  `skipEmptyDirs` int unsigned NOT NULL DEFAULT '1',
  `skipEmptyFiles` int unsigned NOT NULL DEFAULT '1',
  `syncToDest` int unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`cruiseDataTransferID`),
  KEY `CruiseDataTransferStatus` (`status`),
  KEY `CruiseDataTransferType` (`transferType`),
  CONSTRAINT `CruiseDataTransferStatus` FOREIGN KEY (`status`) REFERENCES `OVDM_Status` (`statusID`),
  CONSTRAINT `CruiseDataTransferType` FOREIGN KEY (`transferType`) REFERENCES `OVDM_TransferTypes` (`transferTypeID`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `OVDM_CruiseDataTransfers`
--

LOCK TABLES `OVDM_CruiseDataTransfers` WRITE;
/*!40000 ALTER TABLE `OVDM_CruiseDataTransfers` DISABLE KEYS */;
INSERT INTO `OVDM_CruiseDataTransfers` VALUES (1,'SSDW','Shoreside Data Warehouse',4,'/vault/Shoreside',0,'','','','','','','','104.155.136.229','mt',0,'dragon',2,1,1,0,128,0,0,'0','0',1,1,0),(2,'GTA','Google Transfer Appliance (GTA)',1,'/net/GTA',1,'','','','','','','','','',0,'',1,1,0,1555,0,1,0,'36,38,37,39','',0,0,0),(10,'soi_data2','Archive on soi_data2',1,'/mnt/soi_data2',1,'','','','','','','','','',0,'',2,0,0,0,0,1,0,'36,38,37,39','',0,0,0),(11,'soi_data3','Archive on soi_data3',1,'/mnt/soi_data3',1,'','','','','','','','','',0,'',1,1,0,1558,0,1,0,'36,38,37,39','',0,0,0),(12,'soi_data4','Archive on soi_data4',1,'/mnt/soi_data4',1,'','','','','','','','','',0,'',3,0,0,0,0,1,0,'36,38,37,39','',0,0,0),(19,'soi_data4_test','Archive on soi_data4 test',1,'/mnt/soi_data4/openvdm_',0,'','','','','','','','','',0,'',2,0,0,0,0,1,0,'25,35,30,31,5,6,8,41,32,33,43,9,11,42,12,48,15,21,16,17,40,18,19,46,36,38,37,39,2,14,47,44,20,22,1,29,45','2,3,6,4,7,5,1',0,0,0);
/*!40000 ALTER TABLE `OVDM_CruiseDataTransfers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `OVDM_ExtraDirectories`
--

DROP TABLE IF EXISTS `OVDM_ExtraDirectories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `OVDM_ExtraDirectories` (
  `extraDirectoryID` int unsigned NOT NULL AUTO_INCREMENT,
  `name` tinytext NOT NULL,
  `longName` tinytext,
  `destDir` tinytext NOT NULL,
  `enable` tinyint(1) DEFAULT '0',
  `required` tinyint(1) NOT NULL DEFAULT '0',
  `cruiseOrLowering` int unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`extraDirectoryID`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `OVDM_ExtraDirectories`
--

LOCK TABLES `OVDM_ExtraDirectories` WRITE;
/*!40000 ALTER TABLE `OVDM_ExtraDirectories` DISABLE KEYS */;
INSERT INTO `OVDM_ExtraDirectories` VALUES (1,'Transfer_Logs','Transfer Logs','OpenVDM/TransferLogs',1,1,0),(2,'Dashboard_Data','Dashboard Data','OpenVDM/DashboardData',1,1,0),(3,'From_PublicData','Files copied from ParticipantData share','ParticipantData',1,1,0),(4,'Sealog_Falkor','Sealog - Vessel','Falkor_too/Raw/Sealog',1,0,0),(5,'Tracklines','Cruise Tracklines','OpenVDM/Tracklines',1,0,0),(6,'ROV_OpenRVDAS_Data','Cropped OpenRVDAS data for ROV dives','OpenRVDAS',1,0,1),(7,'Sealog_ROV','Sealog - SuBastian','Sealog',1,0,1);
/*!40000 ALTER TABLE `OVDM_ExtraDirectories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `OVDM_Gearman`
--

DROP TABLE IF EXISTS `OVDM_Gearman`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `OVDM_Gearman` (
  `jobID` int unsigned NOT NULL AUTO_INCREMENT,
  `jobHandle` tinytext,
  `jobKnown` tinyint unsigned DEFAULT '1',
  `jobRunning` tinyint unsigned DEFAULT '1',
  `jobNumerator` int DEFAULT '0',
  `jobDenominator` int DEFAULT '0',
  `jobName` tinytext,
  `jobPid` int unsigned DEFAULT NULL,
  PRIMARY KEY (`jobID`)
) ENGINE=InnoDB AUTO_INCREMENT=8709459 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `OVDM_Gearman`
--

LOCK TABLES `OVDM_Gearman` WRITE;
/*!40000 ALTER TABLE `OVDM_Gearman` DISABLE KEYS */;
INSERT INTO `OVDM_Gearman` VALUES (8709219,'H:OpenVDM-VM.falkortoo.org:751106',1,1,89,100,'Transfer for soi_data3',1558),(8709453,'H:OpenVDM-VM.falkortoo.org:751356',1,1,2,10,'Transfer for GTA',1555);
/*!40000 ALTER TABLE `OVDM_Gearman` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `OVDM_Links`
--

DROP TABLE IF EXISTS `OVDM_Links`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `OVDM_Links` (
  `linkID` int unsigned NOT NULL AUTO_INCREMENT,
  `name` tinytext NOT NULL,
  `url` tinytext NOT NULL,
  `enable` tinyint(1) NOT NULL DEFAULT '0',
  `private` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`linkID`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `OVDM_Links`
--

LOCK TABLES `OVDM_Links` WRITE;
/*!40000 ALTER TABLE `OVDM_Links` DISABLE KEYS */;
INSERT INTO `OVDM_Links` VALUES (1,'Supervisord','http://{hostIP}:9001',1,1),(3,'Cruise Data','http://{hostIP}/CruiseData/{cruiseID}/',1,0),(4,'Participant Data','http://{hostIP}/ParticipantData/',0,0),(5,'Visitor Information','http://{hostIP}/VisitorInformation/',1,0),(6,'MapProxy','http://{hostIP}/mapproxy/demo/',1,0),(7,'ScienceData','http://{hostIP}/ScienceData',0,0);
/*!40000 ALTER TABLE `OVDM_Links` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `OVDM_ShipToShoreTransfers`
--

DROP TABLE IF EXISTS `OVDM_ShipToShoreTransfers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `OVDM_ShipToShoreTransfers` (
  `shipToShoreTransferID` int unsigned NOT NULL AUTO_INCREMENT,
  `name` tinytext,
  `longName` tinytext,
  `priority` int DEFAULT NULL,
  `collectionSystem` int unsigned DEFAULT NULL,
  `extraDirectory` int unsigned DEFAULT NULL,
  `includeFilter` tinytext,
  `enable` tinyint(1) NOT NULL DEFAULT '0',
  `required` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`shipToShoreTransferID`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `OVDM_ShipToShoreTransfers`
--

LOCK TABLES `OVDM_ShipToShoreTransfers` WRITE;
/*!40000 ALTER TABLE `OVDM_ShipToShoreTransfers` DISABLE KEYS */;
INSERT INTO `OVDM_ShipToShoreTransfers` VALUES (1,'DashboardData','Dashboard Data',1,0,2,'*',1,1),(2,'TransferLogs','Transfer Logs',1,0,1,'*',0,1),(3,'MD5Summary','MD5 Summary',1,0,0,'{md5_summary_fn},{md5_summary_md5_fn}',1,1),(4,'OVDM_Config','OpenVDM Configuration',1,0,0,'{cruise_config_fn}',1,1),(5,'cruise_tracklines','Cruise Tracklines',1,0,5,'*',1,0);
/*!40000 ALTER TABLE `OVDM_ShipToShoreTransfers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `OVDM_Status`
--

DROP TABLE IF EXISTS `OVDM_Status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `OVDM_Status` (
  `statusID` int unsigned NOT NULL AUTO_INCREMENT,
  `status` tinytext,
  PRIMARY KEY (`statusID`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `OVDM_Status`
--

LOCK TABLES `OVDM_Status` WRITE;
/*!40000 ALTER TABLE `OVDM_Status` DISABLE KEYS */;
INSERT INTO `OVDM_Status` VALUES (1,'Running'),(2,'Idle'),(3,'Error'),(4,'Off'),(5,'Stopping'),(6,'Starting');
/*!40000 ALTER TABLE `OVDM_Status` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `OVDM_Tasks`
--

DROP TABLE IF EXISTS `OVDM_Tasks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `OVDM_Tasks` (
  `taskID` int unsigned NOT NULL AUTO_INCREMENT,
  `name` tinytext NOT NULL,
  `longName` tinytext NOT NULL,
  `cruiseOrLowering` tinyint unsigned NOT NULL DEFAULT '0',
  `status` int unsigned NOT NULL DEFAULT '3',
  `enable` tinyint(1) NOT NULL DEFAULT '0',
  `pid` int unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`taskID`),
  KEY `ProcessStatus` (`status`),
  CONSTRAINT `ProcessStatus` FOREIGN KEY (`status`) REFERENCES `OVDM_Status` (`statusID`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `OVDM_Tasks`
--

LOCK TABLES `OVDM_Tasks` WRITE;
/*!40000 ALTER TABLE `OVDM_Tasks` DISABLE KEYS */;
INSERT INTO `OVDM_Tasks` VALUES (1,'setupNewCruise','Setup New Cruise',0,2,1,0),(2,'finalizeCurrentCruise','Finalize Current Cruise',0,2,1,0),(3,'rebuildMD5Summary','Rebuild MD5 Summary',0,2,1,0),(4,'rebuildDataDashboard','Rebuild Data Dashboard',0,2,1,0),(5,'rebuildCruiseDirectory','Rebuild Cruise Directory',0,2,1,0),(6,'exportOVDMConfig','Re-export the OpenVDM Configuration',0,2,1,0),(7,'rsyncPublicDataToCruiseData','Sync PublicData within Cruise Directory',0,2,1,0),(8,'setupNewLowering','Setup New {lowering_name}',1,2,1,0),(9,'finalizeCurrentLowering','Finalize Current {lowering_name}',1,2,1,0),(10,'rebuildLoweringDirectory','Rebuild {lowering_name} Directory',1,2,1,0),(11,'exportLoweringConfig','Re-export the {lowering_name} Configuration',1,2,1,0);
/*!40000 ALTER TABLE `OVDM_Tasks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `OVDM_TransferTypes`
--

DROP TABLE IF EXISTS `OVDM_TransferTypes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `OVDM_TransferTypes` (
  `transferTypeID` int unsigned NOT NULL AUTO_INCREMENT,
  `transferType` tinytext,
  PRIMARY KEY (`transferTypeID`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `OVDM_TransferTypes`
--

LOCK TABLES `OVDM_TransferTypes` WRITE;
/*!40000 ALTER TABLE `OVDM_TransferTypes` DISABLE KEYS */;
INSERT INTO `OVDM_TransferTypes` VALUES (1,'Local Directory'),(2,'Rsync Server'),(3,'SMB Share'),(4,'SSH Server'),(5,'FTP Server');
/*!40000 ALTER TABLE `OVDM_TransferTypes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `OVDM_Users`
--

DROP TABLE IF EXISTS `OVDM_Users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `OVDM_Users` (
  `userID` int unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(255) DEFAULT '',
  `password` varchar(255) DEFAULT '',
  `lastLogin` datetime DEFAULT NULL,
  PRIMARY KEY (`userID`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `OVDM_Users`
--

LOCK TABLES `OVDM_Users` WRITE;
/*!40000 ALTER TABLE `OVDM_Users` DISABLE KEYS */;
INSERT INTO `OVDM_Users` VALUES (1,'mt','$2y$10$mWxxNw5r.GXC8MUdTjwAKOi3sesRUOn8Bjdy/pa8n50iuud1avG6C','2024-02-09 00:45:44');
/*!40000 ALTER TABLE `OVDM_Users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-02-09 15:45:56
-- MySQL dump 10.13  Distrib 8.0.36, for Linux (x86_64)
--
-- Host: localhost    Database: openvdm
-- ------------------------------------------------------
-- Server version	8.0.36-0ubuntu0.22.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `OVDM_Messages`
--

DROP TABLE IF EXISTS `OVDM_Messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `OVDM_Messages` (
  `messageID` int unsigned NOT NULL AUTO_INCREMENT,
  `messageTitle` tinytext NOT NULL,
  `messageBody` text,
  `messageTS` datetime NOT NULL,
  `messageViewed` tinyint(1) NOT NULL,
  PRIMARY KEY (`messageID`)
) ENGINE=InnoDB AUTO_INCREMENT=62175 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-02-09 15:46:03
