#!/usr/bin/perl

require "common.pl";

# -----------------------------------------------

$session->delete();
print $cgi->header();
$template->define(main => "index.html");
$template->parse(main => "main");
$template->print();

exit;
