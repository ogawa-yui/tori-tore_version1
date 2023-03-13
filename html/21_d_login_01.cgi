#!/usr/bin/perl --
#!c:/perl64/bin/perl.exe

use lib qw(pm .);

use strict;
use warnings;

use utf8;
use CGI;
use HTML::Template;
use CGI::Carp( 'fatalsToBrowser' );
use Time::Piece;
use Encode;

use Util;

my $q = CGI->new;
$q->charset( 'UTF-8' );


my $tmpl = &Util::load_html_tmpl('21_d_login_01.tmpl' );


print $q->header;
print $tmpl->output;
