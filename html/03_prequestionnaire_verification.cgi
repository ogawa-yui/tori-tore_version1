#!/usr/bin/perl --
#!c:/perl64/bin/perl.exe

#
#   Pre-questionnaire verification screen
#
#   2020-08-05 by OGAWA, Y.

use lib qw(pm .);

use strict;
use warnings;
use utf8;
use CGI;
use HTML::Template;
use CGI::Carp( 'fatalsToBrowser' );
use Util;

use Time::Piece;

my $q = CGI->new;
$q->charset( 'UTF-8' );

# If you came to this page without logging in
unless ($q->param( 'user' )){  # No user name → Not logged in
	# Display message and exit
	my $tmpl = &Util::load_html_tmpl('not_logged_in_message.tmpl' );
	print $q->header;
	print &Encode::encode('utf-8', $tmpl->output);
	exit; # Terminate all programs
}
my $tmpl = &Util::load_html_tmpl('03_prequestionnaire_verification.tmpl' );

my $user = &Util::form_str_utf8($q, 'user');
$tmpl->param( user => "$user" ); 

# Receive questionnaire responses
my $q1 = &Util::form_str_utf8($q, "q1" );
my $q2 = &Util::form_str_utf8($q, "q2" );
my $q2_1 = &Util::form_str_utf8($q, "q2_1" );
my $q2_2 = &Util::form_str_utf8($q, "q2_2" );
my $q3 = &Util::form_str_utf8($q, "q3" );
my $q4 = &Util::form_str_utf8($q, "q4" );
my $q5 = &Util::form_str_utf8($q, "q5" );
my $q6 = &Util::form_str_utf8($q, "q6" );
my $q7 = &Util::form_str_utf8($q, "q7" );
my $q8 = &Util::form_str_utf8($q, "q8" );
my $q9 = &Util::form_str_utf8($q, "q9" );
my $q9_1 = &Util::form_str_utf8($q, "q9_1" );
my $q9_2 = &Util::form_str_utf8($q, "q9_2" );
my $q9_3 = &Util::form_str_utf8($q, "q9_3" );


my $confirm = &Util::form_str_utf8($q, "confirm" );
my $a1 = &Util::form_str_utf8($q, "a1" );
my $a2_1 = &Util::form_str_utf8($q, "a2_1" );
my $a2_2 = &Util::form_str_utf8($q, "a2_2" );
my $a3 = &Util::form_str_utf8($q, "a3" );
my $a4 = &Util::form_str_utf8($q, "a4" );
my $a5 = &Util::form_str_utf8($q, "a5" );
my $a6 = &Util::form_str_utf8($q, "a6" );
my $a7 = &Util::form_str_utf8($q, "a7" );

my (@a8, @a8_1_or_0);
if ($q->param( "a8_1" )){
	my $a8_1 = &Util::form_str_utf8($q, "a8_1" );
	push @a8, $a8_1;
	push @a8_1_or_0, 1; # In check boxes, 1 for selected, 0 for not selected
}
else{
	push @a8_1_or_0, 0;
}

if ($q->param( "a8_2" )){
	my $a8_2 = &Util::form_str_utf8($q, "a8_2" );
	push @a8, $a8_2;
	push @a8_1_or_0, 1;
}
else{
	push @a8_1_or_0, 0;
}

if ($q->param( "a8_3" )){
	my $a8_3 = &Util::form_str_utf8($q, "a8_3" );
	push @a8, $a8_3;
	push @a8_1_or_0, 1;
}
else{
	push @a8_1_or_0, 0;
}

if ($q->param( "a8_4" )){
	my $a8_4 = &Util::form_str_utf8($q, "a8_4" );
	push @a8, $a8_4;
	push @a8_1_or_0, 1;
}
else{
	push @a8_1_or_0, 0;
}

if ($q->param( "a8_5" )){
	my $a8_5 = &Util::form_str_utf8($q, "a8_5" );
	push @a8, $a8_5;
	push @a8_1_or_0, 1;
}
else{
	push @a8_1_or_0, 0;
}

if ($q->param( "a8_6" )){
	my $a8_6 = &Util::form_str_utf8($q, "a8_6" );
	push @a8, $a8_6;
	push @a8_1_or_0, 1;
}
else{
	push @a8_1_or_0, 0;
}

# その他
my $a8_7;
if ($q->param( "a8_7" )){
	$a8_7 = &Util::form_str_utf8($q, "a8_7" ); 
	$tmpl->param( a8_7_for_display => "$a8_7" ); # Only if there are "others"
}
else{
	$a8_7 = "NA";
}

my $a9_1 = &Util::form_str_utf8($q, "a9_1" );
my $a9_2 = &Util::form_str_utf8($q, "a9_2" );
my $a9_3 = &Util::form_str_utf8($q, "a9_3" );

# その他
my $a9_4;
if ($q->param( "a9_4" )){
	$a9_4 = &Util::form_str_utf8($q, "a9_4" );
	$tmpl->param( a9_4_for_display => "$a9_4" ); # Only if there are "others"
}
else{
	$a9_4 = "NA";
}


my $a8 = join(', ', @a8);
my $a8_1_or_0 = join("\t", @a8_1_or_0);

$tmpl->param( q1 => "$q1" ); 
$tmpl->param( q2 => "$q2" ); 
$tmpl->param( q2_1 => "$q2_1" ); 
$tmpl->param( q2_2 => "$q2_2" ); 
$tmpl->param( q3 => "$q3" ); 
$tmpl->param( q4 => "$q4" ); 
$tmpl->param( q5 => "$q5" ); 
$tmpl->param( q6 => "$q6" ); 
$tmpl->param( q7 => "$q7" ); 
$tmpl->param( q8 => "$q8" ); 
$tmpl->param( q9 => "$q9" ); 
$tmpl->param( q9_1 => "$q9_1" ); 
$tmpl->param( q9_2 => "$q9_2" ); 
$tmpl->param( q9_3 => "$q9_3" ); 

$tmpl->param( a1 => "$a1" ); 
$tmpl->param( confirm => "$confirm" ); 
$tmpl->param( a2_1 => "$a2_1" ); 
$tmpl->param( a2_2 => "$a2_2" ); 
$tmpl->param( a3 => "$a3" ); 
$tmpl->param( a4 => "$a4" ); 
$tmpl->param( a5 => "$a5" ); 
$tmpl->param( a6 => "$a6" ); 
$tmpl->param( a7 => "$a7" ); 
$tmpl->param( a8 => "$a8" ); 
$tmpl->param( a8_7 => "$a8_7" ); 

$tmpl->param( a9_1 => "$a9_1" ); 
$tmpl->param( a9_2 => "$a9_2" ); 
$tmpl->param( a9_3 => "$a9_3" ); 
$tmpl->param( a9_4 => "$a9_4" ); 

$tmpl->param( a8_1_or_0 => "$a8_1_or_0" ); 

print $q->header;
print &Encode::encode('utf-8', $tmpl->output);
