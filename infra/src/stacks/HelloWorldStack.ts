import { Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from "constructs";

interface HelloWorldStackProps extends StackProps {
}

export class HelloWorldStack extends Stack {
  constructor(scope: Construct, id: string, props: HelloWorldStackProps) {
    super(scope, id, props);

    console.log("Hello World!");
  }
}