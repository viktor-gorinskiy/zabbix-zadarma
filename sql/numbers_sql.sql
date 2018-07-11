-- phpMyAdmin SQL Dump
-- version 4.4.15.10
-- https://www.phpmyadmin.net
--
-- Хост: localhost
-- Время создания: Июл 11 2018 г., 08:00
-- Версия сервера: 5.5.56-MariaDB
-- Версия PHP: 5.4.16

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- База данных: `asterisk`
--

-- --------------------------------------------------------

--
-- Структура таблицы `zadarma_numbers`
--

CREATE TABLE IF NOT EXISTS `zadarma_numbers` (
  `id` int(10) NOT NULL,
  `date` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `number` varchar(12) DEFAULT NULL,
  `number_name` varchar(60) DEFAULT NULL,
  `description` varchar(60) NOT NULL DEFAULT '',
  `sip` varchar(80) DEFAULT NULL,
  `start_date` datetime NOT NULL,
  `stop_date` datetime NOT NULL,
  `monthly_fee` int(5) DEFAULT NULL,
  `status` int(1) DEFAULT NULL,
  `channels` int(3) DEFAULT NULL,
  `autorenew` int(1) DEFAULT NULL
) ENGINE=InnoDB AUTO_INCREMENT=205 DEFAULT CHARSET=utf8;


ALTER TABLE `zadarma_numbers`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `number` (`number`),
  ADD KEY `calldate` (`date`),
  ADD KEY `accountcode` (`monthly_fee`);

--
-- AUTO_INCREMENT для сохранённых таблиц
--

--
-- AUTO_INCREMENT для таблицы `zadarma_numbers`
--
ALTER TABLE `zadarma_numbers`
  MODIFY `id` int(10) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=205;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
