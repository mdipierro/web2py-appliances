<?php
/*
  WWW SQL Designer, (C) 2005-2007 Ondra Zara, o.z.fw@seznam.cz

    This file is part of WWW SQL Designer.

    WWW SQL Designer is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    WWW SQL Designer is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with WWW SQL Designer; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
*/

//define('DSN', 'mysql://user:pass@host/database/table');
//define('DSN', 'sqlite://./var/path/to/database.db/table');
define('DSN', 'sqlite://.'.dirname(__FILE__).'/database.db/wwwsqldesigner');

  /**********  DATABASE CONNECTION  **********/
  $dbInfo = parse_url(DSN);
  switch ($dbInfo['scheme']) {
    case 'mysql':
      $dbInfo['path'] = explode('/', $dbInfo['path']);
      $dsn = 'mysql:host=' . $dbInfo['host'] . ';dbname=' . $dbInfo['path'][0];
      $dbLink = new PDO($dsn, $dbInfo['user'], $dbInfo['pass']);
      define('TABLE_NAME', $dbInfo['path'][1]);
      break;

    case 'sqlite':
      $dbLink = new PDO("sqlite:" . dirname($dbInfo['path']));
      define('TABLE_NAME', basename($dbInfo['path']));
      break;
  }
  $dbLink->query("CREATE TABLE IF NOT EXISTS " . TABLE_NAME .
    " (keyword TEXT PRIMARY KEY, data TEXT NOT NULL, dt TEXT NOT NULL);");

  /**********  VARIABLE INITIALIZATION  **********/
  if (isset($_GET['import'])) {
    $action = 1;
  }else if (isset($_GET['show'])) {
    $action = 2;
  } else {
    $action = 0; /* defaultni je export */
  }

  /**********  DATABASE EXECUTION  **********/
  switch ($action) {
    case 0:
      $key = (isset($_POST['key']) ? $_POST['key'] : '');
      $data = (isset($_POST['data']) ? $_POST['data'] : '');
      if (!$key) {
        die();
      } else {
        $now = date("'Y-m-d H:i:s'");
        $key = $dbLink->quote($key);
        if (get_magic_quotes_gpc() || get_magic_quotes_runtime()) {
           $data = stripslashes($data);
        }
        $data = $dbLink->quote($data);
        $sql = "SELECT * FROM " . TABLE_NAME . " WHERE keyword = :key";
        $statement = $dbLink->prepare($sql);
        $statement->execute(array(':key'=>$key));
        $r = $statement->fetchAll();
        if (count($r) > 0) {
          $sql = "UPDATE " . TABLE_NAME . " SET data=:data, dt=:now " .
            "WHERE keyword=:key";
        } else {
          $sql = "INSERT INTO " . TABLE_NAME . " (keyword, data, dt) " .
            "VALUES (:key, :data, :now)";
        }
        $statement = $dbLink->prepare($sql);
        $statement->execute(array(':key'=>$key, ':data'=>$data, ':now'=>$now));
        $statement = null;
      }
    break;

    case 1:
      $key = (isset($_GET['key']) ? $_GET['key'] : '');
      $key = $dbLink->quote($key);
      $sql = "SELECT * FROM " . TABLE_NAME . " WHERE keyword=:key";
      $statement = $dbLink->prepare($sql);
      $statement->execute(array(':key'=>$key));
      foreach ($statement->fetchAll() as $data) {
        echo str_replace(array("\n","\r"),'',$data['data']);
        break;
      }
      $statement = null;
    break;

    case 2:
      $sql = "SELECT keyword, dt FROM " . TABLE_NAME . " ORDER BY dt DESC";
      foreach ($dbLink->query($sql, PDO::FETCH_BOTH) as $row) {
          printf ("%s:  %s\n", $row["dt"], $row["keyword"]);
      }
    break;
  } //endswitch
  $dbLink = null; // close connection
