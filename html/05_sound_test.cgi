#!/usr/bin/perl --
#!c:/perl64/bin/perl.exe

#
#   Sound Source Playback Test Screen
#
#   2020-08-05 by OGAWA, Y.

use lib qw(pm .);

use CGI;

# use CGI::Carp( 'fatalsToBrowser' );
use HTML::Template;

use strict;
use warnings;
use utf8; 

use Util;
use Encode; 
my $Data_Charset = 'utf-8';  


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

my $tmpl = &Util::load_html_tmpl('05_sound_test.tmpl' );


my $user = &Util::form_str_utf8($q, 'user');
$tmpl->param( user => "$user" );

print $q->header;
print &Encode::encode('utf-8', $tmpl->output); 


