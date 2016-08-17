#!/usr/bin/env perl
#
# File: summarize_assessments.pl
# Time-stamp: <2016-07-06 11:17:16 yuki>
# Author: Rasmus Villemoes

use strict;
use warnings;

my @verdicts = map {("$_-bonds")} qw(0ambiguous 0bad_cluster 0major_good_cluster 1all_good 1too_few);
push @verdicts, map {("$_-patterns")} qw(0ambiguous 0bad_cluster 0major_good_cluster 1all_good 1too_few);

my @parameters = qw(max-mp-ratio max-peak L-max-mp-ratio L-max-peak min-obs too-few majority pattern-options);

my %vars;

sub read_assess {
    my $f = shift;
    $f =~ m/step([0-9]+)_assess/
	or die "unexpected file name '$f'";
    my $step = $1;
    open(my $fh, '<', $f)
	or die "cannot open $f: $!";
    while (<$fh>) {
	chomp;
	next unless m/^# @ ([0-9A-Z_a-z-]*)\s*(.*)/;
	my $name = $1;
	my $val = $2;
	$vars{$step}{$name} = $val;
    }
    close($fh);
}

read_assess($_) for (@ARGV);

print join("\t", "step", @verdicts) . "\n";
for my $step (sort {$a <=> $b} keys %vars) {
    my $v = $vars{$step};
    printf "%d", $step;
    for (@verdicts) {
	printf "\t%s", $v->{$_} // "0";
    }
    print "\n";
}

print "\n";
print join("\t", "step", @parameters) . "\n";
for my $step (sort {$a <=> $b} keys %vars) {
    my $v = $vars{$step};
    printf "%d", $step;
    for (@parameters) {
	printf "\t%s", $v->{$_} // "?";
    }
    print "\n";
}
