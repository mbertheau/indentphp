<?php

class a {}
abstract class a {}
final class a {}

class b extends a {}
class b implements a {}
abstract class b implements a1, b1 {}

interface i {}
interface i extends a {}

class a
{
    var $a, $b;
    public $a, $b;
    private $a, $b;
    public static $a;
    var $a = 4, $b;
    public $b, $c = 0xFF, $d = array(array(array()));
    const a = 54, b = 32;

    abstract function a();
    final public function a($b = array(0x9F, 0x9E)) {}
    function &a() { ; }
}
?>
