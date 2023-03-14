#!/usr/bin/perl --
#!c:/perl64/bin/perl.exe

use lib qw(pm .);

use CGI;

use strict;
use warnings;
use utf8;

use CGI::Carp( 'fatalsToBrowser' );
use HTML::Template;
use Time::Piece;


use Par;
use Quiz;
use Util;


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


my $tmpl = &Util::load_html_tmpl('11_count_accuracy.tmpl' );


my $user = &Util::form_str_utf8($q, 'user');
$tmpl->param( user => "$user" ); 


my $adaptive = &Quiz::judge_adaptive($user);
$tmpl->param( adaptive => "$adaptive" ); 


my $data_set = {};


&Quiz::load_bird_info($data_set);

# Read sound source information
# Return value is the number of times the sound source and the number of correct answers, initially 0
# $counts->{MP3}->{}, $counts->{MP3}->{}
my ($counts, $corrects) = &Quiz::load_mp3_info($data_set);

# Find the proficiency score from the response log and store it in the $data_set.
# Get the number of past responses by return value.
# $counts->{TODAY}, $counts->{TOTAL}
# $corrects->{TODAY}, $corrects->{TOTAL}
($counts, $corrects) = &Quiz::load_past_achievement($data_set, $user, $counts, $corrects);

# Species Name Romanization List
my @spp = keys %{$data_set}; 


my @accuracy_rates;
my $i = 1; # Set 1 from the top of the table.

my $heading = "音源の種類</th><th scope='col'>音源</th>
               <th scope='col'>出題数</th><th scope='col'>";

if ($adaptive == 1){
	$heading = $heading."習熟度</th><th scope='col'>ステータス";
}
else{
	$heading = $heading."正解数";
}

my @mp3_licenses;

# Display in a table on the screen in order of PRIORITY
foreach my $sp (sort {$data_set->{$a}{PRIORITY} 
	                       <=> $data_set->{$b}{PRIORITY}} @spp) {
    my $MP3_ref = $data_set->{$sp}->{MP3};
    my @mp3s = keys %{$MP3_ref};
    	
    foreach my $mp3 (@mp3s){
    	
    	my $song_type_num = &Quiz::get_song_type_num_for_mp3($data_set, $mp3);
    	my $mp3_str = &Quiz::get_mp3_file_path_name($mp3);
    	my $accuracy_rate = "<tr><td>$i　$song_type_num</td><td>
	                         <audio src='$mp3_str' preload='none'></audio>
	                         </td><td>$counts->{MP3}{$mp3}</td><td>";
	                         
	    # If licensed
        if ($data_set->{$sp}->{MP3}->{$mp3}->{LICENSE} =~ m/by/){
        	
        	my $sp_jp = &Quiz::get_sp_jp_name($data_set, $sp);
        	push @mp3_licenses, "★$song_type_num"."　$data_set->{$sp}->{MP3}->{$mp3}->{LICENSE}<br>";
        	    
        }

    	if ($adaptive == 1){
	
    	    $accuracy_rate = $accuracy_rate."$data_set->{$sp}->{MP3}->{$mp3}->{SCORE}</td><td>";
    	    
    	    if (($counts->{MP3}->{$mp3} > 0 && $data_set->{$sp}->{MP3}->{$mp3}->{SCORE} == 0)
    	        || ($counts->{MP3}->{$mp3} > 6 
    	            && $data_set->{$sp}->{MP3}->{$mp3}->{SCORE} < $Par::QUALIFIED_SCORE)){
    	        push @accuracy_rates, 
    	               $accuracy_rate."<font color='orange'>苦戦中</font></td></tr>";
	        }
	        elsif ($data_set->{$sp}->{MP3}->{$mp3}->{SCORE} >= $Par::QUALIFIED_SCORE){
    	        push @accuracy_rates,
    	               $accuracy_rate."<font color='green'>マスター</font></td></tr>";
	        }
	        else{
	        	push @accuracy_rates, $accuracy_rate."　</td></tr>";
	        }
	        
	    }
	    
	    else{ # Baseline
	    	push @accuracy_rates, $accuracy_rate."$corrects->{MP3}->{$mp3}</td></tr>";
	    }
	    
	    $i++;
	    
	}
}


$tmpl->param( heading => $heading );
$tmpl->param( accuracy_rates => "@accuracy_rates" );
$tmpl->param( mp3_licenses => "@mp3_licenses" );

if ($q->param( 'sp_roman' )){
	my $sp_roman = &Util::form_str_utf8($q, 'sp_roman' );
	$tmpl->param( sp_roman => "$sp_roman" ); 
}


my $content_info = "クイズへ";
my $content_url = "10_quiz.cgi";

my $num_quiz_left_today = &Quiz::get_num_quiz_left_today($counts->{TOTAL});
if ($num_quiz_left_today <= 0){
	$content_info = "保存（ログアウト）";
	$content_url = "00_login_01.cgi";
}

$tmpl->param( content_info => "$content_info" ); 
$tmpl->param( content_url => "$content_url" ); 


print $q->header;
print &Encode::encode('utf-8', $tmpl->output);
