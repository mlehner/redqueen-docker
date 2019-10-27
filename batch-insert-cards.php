<?php

$pdo = new PDO('mysql:dbname=redqueen', 'root');

$file = fopen("php://stdin", "r");

$header = fgets($file);

$queries =<<<SQL
INSERT INTO `cards` (name,code,pin,isActive,created_at,updated_at) VALUES (?, ?, ?, true, NOW(), NOW());
INSERT INTO `card_schedule` (card_id, schedule_id) VALUES (LAST_INSERT_ID(), ?);
SQL;

$createStatement = $pdo->prepare($queries);
$selectStatement = $pdo->prepare('SELECT id FROM cards WHERE code = ?');

while ($fields = fgetcsv($file)) {
  $fields = array_map('trim', $fields);
  list($name, $pin, $code, $schedule_id) = $fields;

  list($last_name, $first_name) = explode(', ', $name, 2);

  echo "name= $first_name $last_name code=$code";

  $fullCode = strtoupper(dechex(21).dechex($code));

  $selectStatement->execute([$fullCode]);

  if (count($selectStatement->fetchAll()) > 0) {
    echo " success=0 err=existing" . PHP_EOL;
  } else {
    $success = $createStatement->execute([implode(' ', [$first_name, $last_name]), $fullCode, $pin, $schedule_id]);
    echo " success=$success" . PHP_EOL;

    $createStatement->closeCursor();

    if (!$success) {
      var_dump($createStatement->errorInfo());
    }
  }

  $selectStatement->closeCursor();
}
