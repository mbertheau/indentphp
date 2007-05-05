<?php
function a()
{
}

function a(array $a)
{
}

function a(array &$a)
{
}

function a(MyClass $a)
{
}

function a(MyClass &$a)
{
}

function a($a = 4)
{
}

function a($a = 4.0)
{
}

function a($a = 4.)
{
}

function a($a = .4)
{
}

function a($a = 0x09F911029D74E35BD84156C5635688C0)
{
}

function a($a = 4e+4)
{
}

function a($a = 4e-4)
{
}

function a($a = .4e-4)
{
}

function a($a = "f'oo")
{
}

function a($a = "f\"o'o")
{
}

function a($a = 'f"oo')
{
}

function a($a = 'f"o\'o')
{
}

function a($a = __LINE__)
{
}

function a($a = __FILE__)
{
}

function a($a = __CLASS__)
{
}

function a($a = __METHOD__)
{
}

function a($a = __FUNCTION__)
{
}

function a($a = CONSTANT)
{
}

function a($a = 4)
{
}

function a($a = -4)
{
}

function a($a = MyClass::MY_CONSTANT)
{
}

function a($a = array())
{
}

function a($a = array(4))
{
}

function a($a = array(4))
{
}

function a($a = array(4 => 4))
{
}

function a($a = array(4 => array(4 => array(4))))
{
}

function a($b = array("foobar" => "barbaz", "quux" => "dragons!"))
{
}

?>
