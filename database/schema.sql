CREATE DATABASE IF NOT EXISTS `queryscale`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `queryscale`;

DROP TABLE IF EXISTS `Transactions`;
DROP TABLE IF EXISTS `Accounts`;
DROP TABLE IF EXISTS `Loans`;
DROP TABLE IF EXISTS `Customers`;
DROP TABLE IF EXISTS `Branches`;

CREATE TABLE `Branches` (
    `branch_id` INT NOT NULL AUTO_INCREMENT,
    `branch_name` VARCHAR(150) NOT NULL,
    `ifsc_code` VARCHAR(20) NOT NULL,
    `city` VARCHAR(100) NOT NULL,
    PRIMARY KEY (`branch_id`),
    UNIQUE KEY `uq_branches_ifsc` (`ifsc_code`),
    KEY `idx_branches_city` (`city`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `Customers` (
    `customer_id` BIGINT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(150) NOT NULL,
    `dob` DATE NOT NULL,
    `kyc_status` VARCHAR(30) NOT NULL,
    `branch_id` INT NOT NULL,
    PRIMARY KEY (`customer_id`),
    CONSTRAINT `fk_customers_branch`
        FOREIGN KEY (`branch_id`) REFERENCES `Branches` (`branch_id`)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    KEY `idx_customers_branch_id` (`branch_id`),
    KEY `idx_customers_kyc_status` (`kyc_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `Accounts` (
    `account_id` BIGINT NOT NULL AUTO_INCREMENT,
    `customer_id` BIGINT NOT NULL,
    `account_type` VARCHAR(50) NOT NULL,
    `balance` DECIMAL(18,2) NOT NULL DEFAULT 0.00,
    `branch_id` INT NOT NULL,
    PRIMARY KEY (`account_id`),
    CONSTRAINT `fk_accounts_customer`
        FOREIGN KEY (`customer_id`) REFERENCES `Customers` (`customer_id`)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT `fk_accounts_branch`
        FOREIGN KEY (`branch_id`) REFERENCES `Branches` (`branch_id`)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    KEY `idx_accounts_customer_id` (`customer_id`),
    KEY `idx_accounts_branch_id` (`branch_id`),
    KEY `idx_accounts_account_type` (`account_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `Transactions` (
    `txn_id` BIGINT NOT NULL AUTO_INCREMENT,
    `account_id` BIGINT NOT NULL,
    `amount` DECIMAL(18,2) NOT NULL,
    `txn_type` VARCHAR(30) NOT NULL,
    `txn_date` DATE NOT NULL,
    PRIMARY KEY (`txn_id`),
    CONSTRAINT `fk_transactions_account`
        FOREIGN KEY (`account_id`) REFERENCES `Accounts` (`account_id`)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    KEY `idx_transactions_account_id` (`account_id`),
    KEY `idx_transactions_txn_date` (`txn_date`),
    KEY `idx_transactions_type_date` (`txn_type`, `txn_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `Loans` (
    `loan_id` BIGINT NOT NULL AUTO_INCREMENT,
    `customer_id` BIGINT NOT NULL,
    `loan_type` VARCHAR(50) NOT NULL,
    `principal` DECIMAL(18,2) NOT NULL,
    `status` VARCHAR(30) NOT NULL,
    PRIMARY KEY (`loan_id`),
    CONSTRAINT `fk_loans_customer`
        FOREIGN KEY (`customer_id`) REFERENCES `Customers` (`customer_id`)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    KEY `idx_loans_customer_id` (`customer_id`),
    KEY `idx_loans_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
