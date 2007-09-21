BEGIN;
ALTER TABLE `et_experiment` DROP FOREIGN KEY `status_id_refs_id_8bc36f5`;
DROP TABLE `et_experimentstatus`;
ALTER TABLE `et_participant` DROP FOREIGN KEY `status_id_refs_id_331dc4b1`;
DROP TABLE `et_participantstatus`;
ALTER TABLE `et_sessionlog` DROP FOREIGN KEY `session_id_refs_id_455b0633`;
ALTER TABLE `et_sessionvar` DROP FOREIGN KEY `experimentSession_id_refs_id_8b85b84`;
ALTER TABLE `et_participant` DROP FOREIGN KEY `experimentSession_id_refs_id_6799173`;
DROP TABLE `et_experimentsession`;
ALTER TABLE `et_experimentcomponents` DROP FOREIGN KEY `experiment_id_id_refs_id_ddebe0f`;
DROP TABLE `et_experiment`;
DROP TABLE `et_experimentsessionstatus`;
DROP TABLE `et_experimentcomponents`;
DROP TABLE `et_sessionlog`;
DROP TABLE `et_component`;
DROP TABLE `et_componenttypes`;
DROP TABLE `et_sessionvar`;
DROP TABLE `et_participant`;
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
CREATE TABLE `et_sessionvar` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `experimentSession_id` integer NOT NULL,
    `key` longtext NOT NULL,
    `value` longtext NOT NULL
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
CREATE TABLE `et_sessionlog` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `participant_id` integer NOT NULL REFERENCES `et_participant` (`id`),
    `component_id` integer NOT NULL REFERENCES `et_component` (`id`),
    `session_id` integer NOT NULL,
    `timestamp` datetime NOT NULL,
    `messageType` longtext NOT NULL,
    `messageText` longtext NOT NULL
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
    `maxPlayers` integer NOT NULL,
    `xValue` integer NOT NULL,
    `yValue` integer NOT NULL
);
ALTER TABLE `et_experimentcomponents` ADD CONSTRAINT experiment_id_id_refs_id_ddebe0f FOREIGN KEY (`experiment_id_id`) REFERENCES `et_experiment` (`id`);
CREATE TABLE `et_experimentsession` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `experiment_id_id` integer NOT NULL REFERENCES `et_experiment` (`id`),
    `status_id` integer NOT NULL REFERENCES `et_experimentsessionstatus` (`id`),
    `dateStarted` date NOT NULL,
    `dateEnded` date NULL
);
ALTER TABLE `et_participant` ADD CONSTRAINT experimentSession_id_refs_id_6799173 FOREIGN KEY (`experimentSession_id`) REFERENCES `et_experimentsession` (`id`);
ALTER TABLE `et_sessionvar` ADD CONSTRAINT experimentSession_id_refs_id_8b85b84 FOREIGN KEY (`experimentSession_id`) REFERENCES `et_experimentsession` (`id`);
ALTER TABLE `et_sessionlog` ADD CONSTRAINT session_id_refs_id_455b0633 FOREIGN KEY (`session_id`) REFERENCES `et_experimentsession` (`id`);
CREATE TABLE `et_participantstatus` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `statusText` varchar(100) NOT NULL
);
ALTER TABLE `et_participant` ADD CONSTRAINT status_id_refs_id_331dc4b1 FOREIGN KEY (`status_id`) REFERENCES `et_participantstatus` (`id`);
CREATE TABLE `et_experimentstatus` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `statusText` varchar(100) NOT NULL
);
ALTER TABLE `et_experiment` ADD CONSTRAINT status_id_refs_id_8bc36f5 FOREIGN KEY (`status_id`) REFERENCES `et_experimentstatus` (`id`);
CREATE INDEX `et_participant_status_id` ON `et_participant` (`status_id`);
CREATE INDEX `et_participant_experimentSession_id` ON `et_participant` (`experimentSession_id`);
CREATE INDEX `et_sessionvar_experimentSession_id` ON `et_sessionvar` (`experimentSession_id`);
CREATE INDEX `et_component_componentType_id` ON `et_component` (`componentType_id`);
CREATE INDEX `et_sessionlog_participant_id` ON `et_sessionlog` (`participant_id`);
CREATE INDEX `et_sessionlog_component_id` ON `et_sessionlog` (`component_id`);
CREATE INDEX `et_sessionlog_session_id` ON `et_sessionlog` (`session_id`);
CREATE INDEX `et_experimentcomponents_experiment_id_id` ON `et_experimentcomponents` (`experiment_id_id`);
CREATE INDEX `et_experimentcomponents_component_id_id` ON `et_experimentcomponents` (`component_id_id`);
CREATE INDEX `et_experiment_status_id` ON `et_experiment` (`status_id`);
CREATE INDEX `et_experimentsession_experiment_id_id` ON `et_experimentsession` (`experiment_id_id`);
CREATE INDEX `et_experimentsession_status_id` ON `et_experimentsession` (`status_id`);
COMMIT;
