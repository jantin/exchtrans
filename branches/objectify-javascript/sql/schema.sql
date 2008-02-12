BEGIN;
CREATE TABLE `et_participant` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(100) NULL,
    `status_id` integer NOT NULL,
    `experimentSession_id` integer NOT NULL,
    `dateCreated` date NOT NULL,
    `currentComponent` integer NULL,
    `currentIteration` integer NULL,
    `cumulativePoints` integer NULL,
    `number` integer NOT NULL,
    `identityLetter` varchar(1) NOT NULL
);
CREATE TABLE `et_log_nex` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `sid` integer NOT NULL,
    `cid` integer NOT NULL,
    `componentIndex` integer NOT NULL,
    `roundIndex` integer NOT NULL,
    `offerIndex` integer NOT NULL,
    `participantName` longtext NOT NULL,
    `participantPartner` longtext NOT NULL,
    `startingX` integer NOT NULL,
    `startingY` integer NOT NULL,
    `initiatedOffer` longtext NOT NULL,
    `xLoss` integer NOT NULL,
    `xGain` integer NOT NULL,
    `yLoss` integer NOT NULL,
    `yGain` integer NOT NULL,
    `xValue` integer NOT NULL,
    `yValue` integer NOT NULL,
    `outcome` longtext NOT NULL,
    `nonBinding` longtext NOT NULL,
    `followedThrough` longtext NULL,
    `pointChange` integer NULL,
    `timestamp` datetime NOT NULL
);
CREATE TABLE `et_log_rex` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `sid` integer NOT NULL,
    `cid` integer NOT NULL,
    `componentIndex` integer NOT NULL,
    `roundIndex` integer NOT NULL,
    `participantName` longtext NOT NULL,
    `participantPartner` longtext NOT NULL,
    `startingX` integer NOT NULL,
    `startingY` integer NOT NULL,
    `xLoss` integer NOT NULL,
    `xGain` integer NOT NULL,
    `yLoss` integer NOT NULL,
    `yGain` integer NOT NULL,
    `xValue` integer NOT NULL,
    `yValue` integer NOT NULL,
    `requiredGift` longtext NOT NULL,
    `pointChange` integer NOT NULL,
    `timestamp` datetime NOT NULL
);
CREATE TABLE `et_componenttypes` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `componentType` varchar(255) NOT NULL,
    `kickoffFunction` varchar(255) NOT NULL,
    `editTemplate` varchar(255) NOT NULL,
    `kickoffTemplate` varchar(255) NOT NULL
);
CREATE TABLE `et_component` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(255) NOT NULL,
    `description` longtext NULL,
    `parameters` longtext NULL,
    `dateCreated` date NOT NULL,
    `dateModified` date NOT NULL,
    `componentType_id` integer NOT NULL REFERENCES `et_componenttypes` (`id`),
    `displayName` varchar(255) NULL
);
CREATE TABLE `et_log_components` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `sid` integer NOT NULL,
    `cid` integer NOT NULL,
    `componentType` longtext NOT NULL,
    `componentName` longtext NOT NULL,
    `componentDescription` longtext NULL,
    `componentParameters` longtext NOT NULL,
    `componentIndex` integer NULL,
    `timestamp` datetime NOT NULL
);
CREATE TABLE `et_log_session` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `sid` integer NOT NULL,
    `eid` integer NOT NULL,
    `experimentName` longtext NOT NULL,
    `experimentDescription` longtext NULL,
    `minPlayers` integer NOT NULL,
    `maxPlayers` integer NOT NULL,
    `playerCount` integer NOT NULL,
    `startTime` datetime NOT NULL,
    `endTime` datetime NULL,
    `exitMessage` longtext NULL,
    `timestamp` datetime NOT NULL
);
CREATE TABLE `et_experimentcomponents` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `experiment_id_id` integer NOT NULL,
    `component_id_id` integer NOT NULL REFERENCES `et_component` (`id`),
    `order` integer NOT NULL,
    `iterations` integer NOT NULL
);
CREATE TABLE `et_experimentsessionstatus` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `statusText` varchar(100) NOT NULL
);
CREATE TABLE `et_experiment` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(100) NOT NULL,
    `description` longtext NOT NULL,
    `status_id` integer NOT NULL,
    `dateCreated` date NOT NULL,
    `dateModified` date NOT NULL,
    `minPlayers` integer NOT NULL,
    `maxPlayers` integer NOT NULL
);
ALTER TABLE `et_experimentcomponents` ADD CONSTRAINT experiment_id_id_refs_id_ddebe0f FOREIGN KEY (`experiment_id_id`) REFERENCES `et_experiment` (`id`);
CREATE TABLE `et_log_matcher` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `sid` integer NOT NULL,
    `cid` integer NOT NULL,
    `componentIndex` integer NOT NULL,
    `deciderName` longtext NOT NULL,
    `deciderPartner` longtext NOT NULL,
    `deciderChoice` longtext NOT NULL,
    `timestamp` datetime NOT NULL
);
CREATE TABLE `et_experimentsession` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `experiment_id_id` integer NOT NULL REFERENCES `et_experiment` (`id`),
    `status_id` integer NOT NULL REFERENCES `et_experimentsessionstatus` (`id`),
    `dateStarted` date NOT NULL,
    `dateEnded` date NULL
);
ALTER TABLE `et_participant` ADD CONSTRAINT experimentSession_id_refs_id_6799173 FOREIGN KEY (`experimentSession_id`) REFERENCES `et_experimentsession` (`id`);
CREATE TABLE `et_sessionvar` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `experimentSession_id` integer NOT NULL REFERENCES `et_experimentsession` (`id`),
    `key` longtext NOT NULL,
    `value` longtext NOT NULL,
    `unread` bool NOT NULL
);
CREATE TABLE `et_log_participants` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `sid` integer NOT NULL,
    `participantName` longtext NOT NULL,
    `participantNumber` integer NOT NULL,
    `participantLetter` longtext NOT NULL,
    `cumulativePoints` integer NULL,
    `timestamp` datetime NOT NULL
);
CREATE TABLE `et_participantstatus` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `statusText` varchar(100) NOT NULL
);
ALTER TABLE `et_participant` ADD CONSTRAINT status_id_refs_id_331dc4b1 FOREIGN KEY (`status_id`) REFERENCES `et_participantstatus` (`id`);
CREATE TABLE `et_log_questionnaire` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `sid` integer NOT NULL,
    `cid` integer NOT NULL,
    `componentIndex` integer NOT NULL,
    `participantName` longtext NOT NULL,
    `questionType` longtext NOT NULL,
    `questionText` longtext NOT NULL,
    `questionResponse` longtext NULL,
    `timestamp` datetime NOT NULL
);
CREATE TABLE `et_experimentstatus` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `statusText` varchar(100) NOT NULL
);
ALTER TABLE `et_experiment` ADD CONSTRAINT status_id_refs_id_8bc36f5 FOREIGN KEY (`status_id`) REFERENCES `et_experimentstatus` (`id`);
CREATE INDEX `et_participant_status_id` ON `et_participant` (`status_id`);
CREATE INDEX `et_participant_experimentSession_id` ON `et_participant` (`experimentSession_id`);
CREATE INDEX `et_component_componentType_id` ON `et_component` (`componentType_id`);
CREATE INDEX `et_experimentcomponents_experiment_id_id` ON `et_experimentcomponents` (`experiment_id_id`);
CREATE INDEX `et_experimentcomponents_component_id_id` ON `et_experimentcomponents` (`component_id_id`);
CREATE INDEX `et_experiment_status_id` ON `et_experiment` (`status_id`);
CREATE INDEX `et_experimentsession_experiment_id_id` ON `et_experimentsession` (`experiment_id_id`);
CREATE INDEX `et_experimentsession_status_id` ON `et_experimentsession` (`status_id`);
CREATE INDEX `et_sessionvar_experimentSession_id` ON `et_sessionvar` (`experimentSession_id`);
COMMIT;
